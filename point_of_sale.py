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


class pos_order_line(osv.osv):
    _inherit = "pos.order.line"
    def price_by_product(self, cr, uid, ids, pricelist, product_id, qty=0, partner_id=False):
        riga_listino = self.pool.get('product.pricelist').price_get_adhoc(cr, uid, [pricelist], product_id, qty, partner_id, context=False)
        if riga_listino:
            unit_price = riga_listino['prezzo_netto']
        else:
            unit_price = super(pos_order_line, self).price_by_product(cr, uid, ids, pricelist, product_id, qty, partner_id)
        
        return unit_price

pos_order_line()
