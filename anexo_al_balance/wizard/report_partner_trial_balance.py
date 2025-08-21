from odoo import fields, models
from odoo import exceptions, _

class BalanceReport(models.TransientModel):
    _inherit = 'account.common.account.report'
    _name = 'anexo_al_balance.report.partner_trial_balance'
    _description = 'Partner Trial Balance Report'

    date_from = fields.Date(string='Start Date', required=True)
    #TODO se sobreescribe relacion
    #por tamano en base de datos
    journal_ids = fields.Many2many('account.journal', 'anexo_al_balance_reportptr_journal_rel', 'account_id', 'journal_id', string='Journals', required=True)
    default_unknown_partner = fields.Many2one('res.partner', string='Default Unknown Partner', required=True)
    
    def _print_report(self, data):
        data = self.pre_print_report(data)
        data['form'].update({
            'default_unknown_partner_id': self.default_unknown_partner.id
        })
        records = self.env[data['model']].browse(data.get('ids', []))
        action = self.env['report'].get_action(records, 'anexo_al_balance.report_partner_trial_balance', data=data)
        return action


