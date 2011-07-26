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


class sale_order_line(osv.osv):
    _inherit = "sale.order.line"

    _columns = {
                "string_discount" : fields.char("Stringa Sconto", size=20, required=False, translate=True, help="Inserire una stringa sconto tipo:50+10+5"),
                'prezzo_netto': fields.float('Prezzo', required=True, digits_compute=dp.get_precision('Sale Price')),
                }
    
    def on_change_stringa_sc(self, cr, uid, ids, value, price_unit, context=None):
        #import pdb;pdb.set_trace()
        if value:
            lista_sconti = value.split("+")
            sconto = float(100)
            for scontoStr in lista_sconti:
                if scontoStr <> "+":
                    sconto = sconto - (sconto * float(scontoStr) / 100)
            sconto = (100 - sconto)
        else:
            sconto = 0
        prezzo = price_unit - (price_unit * sconto / 100)
        return  {'value': {'discount': sconto, 'prezzo_netto': prezzo}}
    
    
    def Calcolo_Sconto(self, cr, uid, ids, value, context=None):
        
        # import pdb;pdb.set_trace()
        if value:
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
        else:
            sconto = 0
        
        return  {'value': {'discount': sconto}}
  
 
    
    
    def Calcolo_netto(self, cr, uid, ids, value, price_unit, context=None):
        #import pdb;pdb.set_trace()
        if value:
            prezzo = price_unit - (price_unit * value / 100)
        else:
            prezzo = 0
        return  {'value': {'prezzo_netto': prezzo}}    
    
    def on_change_price_unit(self, cr, uid, ids, value, discount, context=None):
        #import pdb;pdb.set_trace()      
        if value:
            prezzo = value - (value * discount / 100)
        else:
            prezzo = 0
        return  {'value': {'prezzo_netto': prezzo}}  

    def product_id_change(self, cr, uid, ids, pricelist, product, qty=0, uom=False, qty_uos=0, uos=False, name='', partner_id=False, lang=False, update_tax=True, date_order=False, packaging=False, fiscal_position=False, flag=False):

        reso = super(sale_order_line, self).product_id_change(cr, uid, ids, pricelist, product, qty, uom, qty_uos, uos, name, partner_id, lang, update_tax, date_order, packaging, fiscal_position, flag)
        # segue prima la strada normale poi si cerca il listino secondo le vecchie regole ad-Hoc
        result = reso['value']
        domain = reso['domain']
        warning = ''
        #import pdb;pdb.set_trace()
        if product:
         #import pdb;pdb.set_trace()
         riga_listino = self.pool.get('product.pricelist').price_get_adhoc(cr, uid, [pricelist], product, qty, partner_id, context=False)
         if riga_listino:
            # assegna i campi che ha a disposizione
              result.update({'price_unit':riga_listino['prezzo']})
              result.update({'string_discount':riga_listino['sconti']})
              result.update({'discount':riga_listino['discount_riga']})
              result.update({'prezzo_netto':riga_listino['prezzo_netto']})          
        
        return {'value': result, 'domain': domain, 'warning': warning}
    
sale_order_line()
