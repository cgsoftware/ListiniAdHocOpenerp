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
        # legge i prezzi dal listino
        #import pdb;pdb.set_trace()
        res = {}
        if partner:
            # to do c'è il partner cerca quindi nel contratto che vince sul listino
            pass
        if not res:
            # non ha trovato nulla legato al contratto cerca puramente il listino
                price_id = self.pool.get('listini').search(cr, uid, [('product_id', '=', prod_id), ('listino_id', '=', ids[0])], context=context)[0]
                if price_id:
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
    
    _columns = {
                'righe_listini': fields.one2many('listini', 'product_id', 'Righe Listini', required=False),
                'righe_ultimi_prezzi': fields.one2many('ultimi.prezzi', 'product_id', 'Righe Ultimi Prezzi', required=False),
                'price_default': fields.function(_product_price_defa, method=True, type='float', string='Prezzo Netto Default', digits_compute=dp.get_precision('Sale Price')),
                }

product_product()


class res_partner(osv.osv):
    _inherit = 'res.partner'
    
    _columns = {
                'righe_contratti': fields.one2many('contratti.partner', 'partner_id', 'Condizioni Contrattuali', required=False),
                
                }

res_partner()




