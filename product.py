# -*- encoding: utf-8 -*-

import netsvc
import pooler, tools
import math
from tools.translate import _
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import decimal_precision as dp
import time


from osv import fields, osv



class product_pricelist(osv.osv):
    _inherit = "product.pricelist"
    _columns = {
                    'default_price': fields.boolean('Default', help="Prezzo da visualizzare in automatico nelle ricerche"),
                    }
        
    def price_get_adhoc(self, cr, uid, ids, prod_id, qty, partner=None, context=None):
        # manca il controllo sulle date di attivazione da a
        # legge i prezzi dal listino
        #import pdb;pdb.set_trace()
        res = {}
        if partner:
            # to do c'è il partner cerca quindi nel contratto che vince sul listino
            #import pdb;pdb.set_trace()
            res = self.pool.get('contratti.partner').cerca_contratto(cr, uid, ids, partner, prod_id, qty)
            #import pdb;pdb.set_trace()
        if not res:
            # non ha trovato nulla legato al contratto cerca puramente il listino
                price_id = self.pool.get('listini').search(cr, uid, [('product_id', '=', prod_id), ('listino_id', '=', ids[0])], context=context)
                if price_id:
                 price_id = price_id[0]
                 price_rec = self.pool.get('listini').browse(cr, uid, [price_id])[0]
                 # res = price_rec
                 res.update({'prezzo_netto':price_rec.prezzo_netto})
                 res.update({'sconti':price_rec.sconti})
                 res.update({'discount_riga':price_rec.discount_riga})
                 res.update({'prezzo':price_rec.prezzo})
                else:
                    res = {}
        return res        
 
        
product_pricelist()    


class listini(osv.osv):
    
   _name = "listini"
   _description = "Listini prezzi Articoli"
   
   _columns = {
               'product_id': fields.many2one('product.product', 'Articolo', required=True, ondelete='cascade', select=True),
               'listino_id': fields.many2one('product.pricelist', 'Pricelist', required=True, help="Listino "),
               'prezzo':fields.float('Prezzo di Vendita', digits=(12, 5)),
               'sconti':fields.char("Sconti", size=20),
               'discount_riga':fields.float('Sconto Totale di Riga', digits=(12, 3)),
               'prezzo_netto':fields.float('Prezzo Netto di Riga', digits=(12, 5)),
               'default_price': fields.boolean('Default', help="Prezzo da visualizzare in automatico nelle ricerche"),

               } 
   
   def Calcolo_Sconto(self, cr, uid, ids, value):
        if value :
            lista_sconti = value.split("+")
            sconto = float(100)
            for scontoStr in lista_sconti:
                if '-' in scontoStr and len(lista_sconti) == 1:
                    #  È IL CASO DI UN UNICO VALORE '-20'
                    ScoMeno = scontoStr.split('-')[1]
                    sconto = sconto + (sconto * float(ScoMeno) / 100)  
                else:              
                 if '-' in scontoStr:
                    First = True
                    for ScoMeno in scontoStr.split('-'):
                        #import pdb;pdb.set_trace()
                        if ScoMeno:
                         if First:
                            First = False
                            sconto = sconto - (sconto * float(ScoMeno) / 100)
                         else:
                            sconto = sconto + (sconto * float(ScoMeno) / 100)                        
                 else:
                    sconto = sconto - (sconto * float(scontoStr) / 100)
                    
            sconto = (100 - sconto)
        else:
            sconto = 0

       
        return sconto
   
   def on_change_prezzo(self, cr, uid, ids, sconto, prezzo): 
       v = {}
       
       if sconto:
           v['prezzo_netto'] = self.calcola_netto(prezzo, sconto) 
       else:
            v['prezzo_netto'] = prezzo
       return  {'value': v}  
   
   def calcola_netto(self, prezzo, sconto):
       return prezzo - (prezzo * sconto / 100)
   
   def on_change_sconti(self, cr, uid, ids, value, prezzo):
       #import pdb;pdb.set_trace()
            v = {}
            sconto = self.Calcolo_Sconto(cr, uid, ids, value)
            v['discount_riga'] = sconto
            v['prezzo_netto'] = self.calcola_netto(prezzo, sconto)          

            return  {'value': v}    
   
   def on_change_listino(self, cr, uid, ids, value):
       #import pdb;pdb.set_trace()
        v = {}
        if value:
            PriceDefault = self.pool.get("product.pricelist").browse(cr, uid, [value])[0].default_price
            v['default_price'] = PriceDefault          


        return  {'value': v}    
   
   
   
listini()

class ultimi_prezzi(osv.osv):
    
   _name = "ultimi.prezzi"
   _description = "Ultimi Prezzi Praticati x Partner"
   
   _columns = {
               'product_id': fields.many2one('product.product', 'Articolo', required=True, ondelete='cascade', select=True),
               'data_documento': fields.date('Data Documento', required=True, readonly=False),
               'partner_id': fields.many2one('res.partner', 'Partner', select=True),
               'qty': fields.float('Quantità (UoM)', digits=(16, 2), required=True, readonly=False , Traslate=True),
               'prezzo':fields.float('Prezzo di Vendita', digits=(12, 5)),
               'sconti':fields.char("Sconti", size=20),
               'discount_riga':fields.float('Sconto Totale di Riga', digits=(12, 3)),
               'prezzo_netto':fields.float('Prezzo Netto di Riga', digits=(12, 5)),

               }
   def calcola_netto(self, prezzo, sconto):
       return prezzo - (prezzo * sconto / 100)
   
   def on_change_prezzo(self, cr, uid, ids, sconto, prezzo): 
       v = {}
       
       if sconto:
           v['prezzo_netto'] = self.calcola_netto(prezzo, sconto) 
       else:
            v['prezzo_netto'] = prezzo
       return  {'value': v}     
   
   def on_change_sconti(self, cr, uid, ids, value, prezzo):
       #import pdb;pdb.set_trace()
        v = {}
        if value :
            lista_sconti = value.split("+")
            sconto = float(100)
            for scontoStr in lista_sconti:
                if '-' in scontoStr :
                    First = True
                    for ScoMeno in scontoStr.split('-'):
                        if First:
                            First = False
                            sconto = sconto - (sconto * float(ScoMeno) / 100)
                        else:
                            sconto = sconto + (sconto * float(ScoMeno) / 100)                        
                else:
                    sconto = sconto - (sconto * float(scontoStr) / 100)
                    
            sconto = (100 - sconto)
            v['discount_riga'] = sconto
            v['prezzo_netto'] = self.calcola_netto(prezzo, sconto)          
        else:
            sconto = 0
            v['discount_riga'] = sconto
            v['prezzo_netto'] = prezzo          
            

        return  {'value': v}     
    
ultimi_prezzi()


class contratti_partner(osv.osv):
    
   _name = "contratti.partner"
   _description = "condizioni contrattuali per partner"
   
   _columns = {
               'partner_id': fields.many2one('res.partner', 'Partner', select=True),
               'product_id': fields.many2one('product.product', 'Articolo', required=False, select=True),
               'categ_id': fields.many2one('product.category', 'Categoria', required=False, domain="[('type','=','normal')]"),
               'fromqty': fields.float('Da Quantità (UoM)', digits=(16, 2), required=False, readonly=False , Traslate=True),
               'toqty': fields.float('A Quantità (UoM)', digits=(16, 2), required=False, readonly=False , Traslate=True),
               'prezzo':fields.float('Prezzo di Vendita', digits=(12, 5)),
               'sconti':fields.char("Sconti", size=20),
               'discount_riga':fields.float('Sconto Totale di Riga', digits=(12, 3)),

               }

   
   def cerca_contratto(self, cr, uid, ids, partner, product, qty):
       
       def _create_parent_category_list(id, lst):
            if not id:
                return []
            parent = product_category_tree.get(id)
            if parent:
                lst.append(parent)
                return _create_parent_category_list(parent, lst)
            else:
                return lst
       
       riga = {}
       product_category_obj = self.pool.get('product.category')
       ids_righe = self.search(cr, uid, [('partner_id', '=', partner)])
       if ids_righe:
           # ci sono righe di contratto 
           product_obj = self.pool.get('product.product').browse(cr, uid, product)
           # product.category:
           product_category_ids = product_category_obj.search(cr, uid, [])
           product_categories = product_category_obj.read(cr, uid, product_category_ids, ['parent_id'])
           product_category_tree = dict([(item['id'], item['parent_id'][0]) for item in product_categories if item['parent_id']])  
           categ_ids = _create_parent_category_list(product_obj.categ_id.id, [product_obj.categ_id.id])
           # cerca l' articolo
           ids_articolo = self.search(cr, uid, [('partner_id', '=', partner), ('product_id', '=', product)])
           if ids_articolo:
               for riga_contr in self.browse(cr, uid, ids_articolo):
                   if qty >= riga_contr.fromqty and qty <= riga_contr.toqty:
                       riga.update({'prezzo_netto':riga_contr.prezzo - (riga_contr.prezzo * riga_contr.discount_riga / 100)})
                       riga.update({'sconti':riga_contr.sconti})
                       riga.update({'discount_riga':riga_contr.discount_riga})
                       riga.update({'prezzo':riga_contr.prezzo})
           if not riga:
               # non ha trovato un articolo interessante
               ids_categ = self.search(cr, uid, [('partner_id', '=', partner), ('categ_id', 'in', categ_ids)])
               if ids_categ:
                   # c'è almeno una definizione per categoria
                   for riga_contr in self.browse(cr, uid, ids_articolo):
                    if qty >= riga_contr.fromqty and qty <= riga_contr.toqty:
                       riga.update({'prezzo_netto':riga_contr.prezzo - (riga_contr.prezzo * riga_contr.discount_riga / 100)})
                       riga.update({'sconti':riga_contr.sconti})
                       riga.update({'discount_riga':riga_contr.discount_riga})
                       riga.update({'prezzo':riga_contr.prezzo})
           if not riga:
                # non ha trovato nulla di interessante per categoria  quindi se c'è una riga di solo c
                # partner la tiene in considerazione altrimenti riga sarà vuota
                for riga_contr in self.browse(cr, uid, ids_righe):
                    if not riga_contr.product_id and not riga_contr.categ_id:
                        # è riga di solo partner in questo caso va bene
                       riga.update({'prezzo_netto':riga_contr.prezzo - (riga_contr.prezzo * riga_contr.discount_riga / 100)})
                       riga.update({'sconti':riga_contr.sconti})
                       riga.update({'discount_riga':riga_contr.discount_riga})
                       riga.update({'prezzo':riga_contr.prezzo})                       
       return riga

   def calcola_netto(self, prezzo, sconto):
       return prezzo - (prezzo * sconto / 100)
   
   
   def on_change_sconti(self, cr, uid, ids, value, prezzo):
       #import pdb;pdb.set_trace()
        v = {}
        if value :
            lista_sconti = value.split("+")
            sconto = float(100)
            for scontoStr in lista_sconti:
                if '-' in scontoStr :
                    First = True
                    for ScoMeno in scontoStr.split('-'):
                        if First:
                            First = False
                            sconto = sconto - (sconto * float(ScoMeno) / 100)
                        else:
                            sconto = sconto + (sconto * float(ScoMeno) / 100)                        
                else:
                    sconto = sconto - (sconto * float(scontoStr) / 100)
                    
            sconto = (100 - sconto)
            v['discount_riga'] = sconto
            v['prezzo_netto'] = self.calcola_netto(prezzo, sconto)          
        else:
            sconto = 0
            v['discount_riga'] = sconto
            v['prezzo_netto'] = prezzo          
            

        return  {'value': v}    
    
   def on_change_prezzo(self, cr, uid, ids, sconto, prezzo): 
       v = {}
       
       if sconto:
           v['prezzo_netto'] = self.calcola_netto(prezzo, sconto) 
       else:
            v['prezzo_netto'] = prezzo
       return  {'value': v}     
    
contratti_partner()


class product_product(osv.osv):
    _inherit = 'product.product'

    
    def _product_price_defa(self, cr, uid, ids, name, arg, context=None):
        # cambia la modalià di calcolo del prezzo da visionare in automatico
        #import pdb;pdb.set_trace()
        res = {}
        if context is None:
            context = {}
        pricelist = context.get('listino', False)
        if not pricelist:
            pricelist = context.get('pricelist', False)
        if not pricelist:
             for id_lot in ids:
                try:
                    price_id = self.pool.get('listini').search(cr, uid, [('product_id', '=', id_lot), ('default_price', '=', True)], context=context)[0]
                    if price_id:
                        price = self.pool.get('listini').browse(cr, uid, [price_id])[0].prezzo_netto
                    else:
                        price = 0.0
                except:
                    price = 0.0
                res[id_lot] = price           
        else:
            # cerco e prendo il prezzo del listino selezionato se non trovo nulla 
            for id_lot in ids:
                try:
                    price_id = self.pool.get('listini').search(cr, uid, [('product_id', '=', id_lot), ('listino_id', '=', pricelist)], context=context)[0]
                    if price_id:
                        price = self.pool.get('listini').browse(cr, uid, [price_id])[0].prezzo_netto
                    else:
                        price = 0.0
                except:
                    price = 0.0
                res[id_lot] = price
                
        for id in ids:
            res.setdefault(id, 0.0)
        return res    
    
    
    def _product_price_defa_iva_inc(self, cr, uid, ids, name, arg, context=None):
        res = {}
        if context is None:
            context = {}
        if ids:
            for product in self.browse(cr, uid, ids):
                # import pdb;pdb.set_trace()
                tasse_ids = self.pool.get('account.fiscal.position').map_tax(cr, uid, False, product.taxes_id)
                if tasse_ids:
                    price_vat = 0
                    for tassa in self.pool.get('account.tax').browse(cr, uid, tasse_ids):
                        price_vat = product.price_default * (1 + tassa.amount)
                        res[product.id] = price_vat
        for id in ids:
            res.setdefault(id, 0.0)

        return res
    
    _columns = {
                'righe_listini': fields.one2many('listini', 'product_id', 'Righe Listini', required=False),
                'righe_ultimi_prezzi': fields.one2many('ultimi.prezzi', 'product_id', 'Righe Ultimi Prezzi', required=False),
                'price_default': fields.function(_product_price_defa, method=True, type='float', string='Prezzo Netto Default', digits_compute=dp.get_precision('Sale Price')),
                'price_default_iva_inc': fields.function(_product_price_defa_iva_inc, method=True, type='float', string='Prezzo Ivato Default', digits_compute=dp.get_precision('Sale Price')),
                }

product_product()


class res_partner(osv.osv):
    _inherit = 'res.partner'
    
    _columns = {
                'righe_contratti': fields.one2many('contratti.partner', 'partner_id', 'Condizioni Contrattuali', required=False),
                
                }

res_partner()




