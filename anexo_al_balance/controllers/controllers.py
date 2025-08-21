# -*- coding: utf-8 -*-
from odoo import http

# class AnexoAlBalance(http.Controller):
#     @http.route('/anexo_al_balance/anexo_al_balance/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/anexo_al_balance/anexo_al_balance/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('anexo_al_balance.listing', {
#             'root': '/anexo_al_balance/anexo_al_balance',
#             'objects': http.request.env['anexo_al_balance.anexo_al_balance'].search([]),
#         })

#     @http.route('/anexo_al_balance/anexo_al_balance/objects/<model("anexo_al_balance.anexo_al_balance"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('anexo_al_balance.object', {
#             'object': obj
#         })