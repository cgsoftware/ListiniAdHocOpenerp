##############################################################################
#    
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.     
#
##############################################################################
{
    "name" : "Gestione Listini Ad-Hoc",
    "version" : "1.0",
    "author" : "C.& G. Software",
    "category" : "sale",
    "description":"""
    Definisce + prezzi listino per articolo, un listino può essere iva inclusa o esclusa, inoltre aggiunge delle regole particolari per cliente lette prima dei 
    listini, e fa si che vengano storicizzati gli ultimi prezzi di per partner in un secondo momento sarà possibile anche ripresentare questa informazione
    nella vendita
    """,
    "depends" : ["base", "product", "sale", "product_visible_discount"],
    "init_xml" : [],
    "demo_xml" : [],
    "update_xml" : ['listini_view.xml', 'security/ir.model.access.csv'],
    "active": False,
    "installable": True
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

