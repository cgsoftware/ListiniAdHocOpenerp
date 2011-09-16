# -*- encoding: utf-8 -*-

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import decimal_precision as dp
import time
import netsvc
import pooler, tools
import math
from tools.translate import _


from osv import fields, osv

class FiscalDocRighe(osv.osv):
    _inherit = "fiscaldoc.righe"
   
    def determina_prezzo_sconti(self, cr, uid, ids, product_id, listino_id, qty, partner_id, uom, data_doc):  
       res = super(FiscalDocRighe, self).determina_prezzo_sconti(cr, uid, ids, product_id, listino_id, qty, partner_id, uom, data_doc)
       if res:
           riga_listino = self.pool.get('product.pricelist').price_get_adhoc(cr, uid, [listino_id], product_id, qty, partner_id, context=False)
           if riga_listino:
               # trovato prezzo
              res.update({'prezzo':riga_listino['prezzo']})
              res.update({'StringaSconto':riga_listino['sconti']})
              res.update({'sconto':riga_listino['discount_riga']})
             # result.update({'prezzo_netto':riga_listino['prezzo_netto']})          
               
       # {'prezzo':new_list_price, 'sconto':sconto, 'StringaSconto':item_String_Discount}
       return res
    
    
FiscalDocRighe()
