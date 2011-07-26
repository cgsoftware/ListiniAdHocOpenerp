# -*- encoding: utf-8 -*-

import netsvc
import pooler, tools
import math

from tools.translate import _

from osv import fields, osv




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

               } 
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
ultimi_prezzi()


class contratti_partner(osv.osv):
    
   _name = "contratti.partner"
   _description = "condizioni contrattuali per partner"
   
   _columns = {
               'partner_id': fields.many2one('res.partner', 'Partner', select=True),
               'product_id': fields.many2one('product.product', 'Articolo', required=False, select=True),
               'categ_id': fields.many2one('product.category', 'Categoria', required=False, domain="[('type','=','normal')]"),
               'fromqty': fields.float('Da Quantità (UoM)', digits=(16, 2), required=False, readonly=False , Traslate=True),
               'fromqty': fields.float('A Quantità (UoM)', digits=(16, 2), required=False, readonly=False , Traslate=True),
               'prezzo':fields.float('Prezzo di Vendita', digits=(12, 5)),
               'sconti':fields.char("Sconti", size=20),
               'discount_riga':fields.float('Sconto Totale di Riga', digits=(12, 3)),

               } 
contratti_partner()


class product_product(osv.osv):
    _inherit = 'product.product'
    
    _columns = {
                'righe_listini': fields.one2many('listini', 'product_id', 'Righe Listini', required=False),
                'righe_ultimi_prezzi': fields.one2many('ultimi.prezzi', 'product_id', 'Righe Ultimi Prezzi', required=False),
                }

product_product()


class res_partner(osv.osv):
    _inherit = 'res.partner'
    
    _columns = {
                'righe_contratti': fields.one2many('contratti.partner', 'partner_id', 'Condizioni Contrattuali', required=False),
                
                }

res_partner()



