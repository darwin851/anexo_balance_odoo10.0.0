import time
import copy
import dateutil.parser
from datetime import timedelta

from odoo import api , models, _
from odoo.exceptions import UserError


class ReportPartnerTrialBalance(models.AbstractModel):
    """
    Basado en `report.account.report_trialbalance`
    genera reporte de prueba con terceros agrupados.
    """
    _name = 'report.anexo_al_balance.report_partner_trial_balance'

    def _prepare_sql(self):
        # Prepare sql query base on selected parameters from wizard
        tables, where_clause, where_params = self.env['account.move.line']._query_get()
        tables = tables.replace('"','')
        if not tables:
            tables = 'account_move_line'
        wheres = [""]
        if where_clause.strip():
            wheres.append(where_clause.strip())
        return (tables, where_clause, where_params, wheres)

    def _fetch_moves_by_account_id(self, accounts):
        account_result = {}
        (tables, where_clause, where_params, wheres) = self._prepare_sql()
        filters = " AND ".join(wheres)
        # compute the balance, debit and credit for the provided accounts
        request = ("SELECT account_id AS id, SUM(debit) AS debit, SUM(credit) AS credit, (SUM(debit) - SUM(credit)) AS balance" +\
                   " FROM " + tables + " WHERE account_id IN %s " + filters + " GROUP BY account_id")
        params = (tuple(accounts.ids),) + tuple(where_params)
        self.env.cr.execute(request, params)
        for row in self.env.cr.dictfetchall():
            account_result[row.pop('id')] = row
        return account_result

    def _fetch_moves_by_account_id_and_partner_id(self, accounts, default_partner_id):
        account_result = {}
        indexes = {}
        (tables, where_clause, where_params, wheres) = self._prepare_sql()
        filters = " AND ".join(wheres)
        # compute the balance, debit and credit for the provided accounts
        request = ("SELECT account_id AS id, account_move_line.partner_id as partner_id, SUM(debit) AS debit, SUM(credit) AS credit, (SUM(debit) - SUM(credit)) AS balance" +\
                   " FROM " + tables + " WHERE account_id IN %s " + filters + " GROUP BY account_id,account_move_line.partner_id")
        params = (tuple(accounts.ids),) + tuple(where_params)
        self.env.cr.execute(request, params)
        
        for row in self.env.cr.dictfetchall():
            rid = row.pop('id')
            partner_id = row.get('partner_id') or default_partner_id
            key = '%d.%d' % (rid, partner_id)
            if not rid in account_result:
                account_result[rid] = []
            account_result[rid].append(row)
            assert not key in indexes
            indexes[key] = len(account_result[rid]) - 1
        
        return (account_result, indexes)
        
    #tomado de: account/report/account_balance.py
    def _get_accounts(self, used_context, accounts, display_account, default_partner_id):
        """ compute the balance, debit and credit for the provided accounts
            :Arguments:
                `accounts`: list of accounts record,
                `display_account`: it's used to display either all accounts or those accounts which balance is > 0
            :Returns a list of dictionary of Accounts with following key and value
                `name`: Account name,
                `code`: Account code,
                `credit`: total amount of credit,
                `debit`: total amount of debit,
                `balance`: total amount of balance,
                `type`: `line` or `subline` or `subtotal`
        """

        account_result = self._fetch_moves_by_account_id(accounts)
        (account_partner_result, _) = self._fetch_moves_by_account_id_and_partner_id(accounts, default_partner_id)
        
        date_to = dateutil.parser.parse(used_context['date_from']) - timedelta(days=1)
        used_context_previous = copy.copy(used_context)
        used_context_previous.update({'date_to': date_to, 'date_from': False})
        account_result_previous = self.with_context(used_context_previous)._fetch_moves_by_account_id(accounts)
        (account_partner_result_previous, account_partner_result_previous_idx) = self.with_context(used_context_previous)._fetch_moves_by_account_id_and_partner_id(accounts, default_partner_id)
        #query all partners
        partners = {}
        for partner in self.env['res.partner'].search([]):
            partners[partner.id] = partner

        def get_partners(account_id):
            vlist = []
            if account_id in account_partner_result.keys():
                    for account_partner in account_partner_result[account.id]:
                        res_partner = dict((fn, 0.0) for fn in ['balance_prev', 'credit', 'debit', 'balance', 'balance_total'])
                        partner_id = account_partner.get('partner_id')
                        if partner_id not in partners:
                            partner_id = default_partner_id
                        
                        if partner_id not in partners:
                            raise UserError(_('Asociado en Elementos de diaro con id %s no ubicado en Asociados, indique un partner por defecto') % (str(partner_id)))
                        res_partner['type'] = 'subline'
                        res_partner['code'] = partners[partner_id].vat
                        res_partner['name'] = partners[partner_id].name
                        res_partner['debit'] = account_partner.get('debit')
                        res_partner['credit'] = account_partner.get('credit')
                        res_partner['balance'] = account_partner.get('balance')
                        res_partner['balance_total'] = res_partner['balance']
                        
                        key = '%d.%d' % (account_id, partner_id)
                        if account_id in account_partner_result_previous and key in account_partner_result_previous_idx:
                            previous = account_partner_result_previous[account_id][account_partner_result_previous_idx[key]]
                            res_partner['balance_prev'] = previous['balance']
                            res_partner['balance_total'] = previous['balance'] + res_partner['balance']
                            
                        vlist.append(res_partner)
            return vlist
            
        account_res = []
        for account in accounts:
            res = dict((fn, 0.0) for fn in ['balance_prev', 'credit', 'debit', 'balance', 'balance_total'])
            currency = account.currency_id and account.currency_id or account.company_id.currency_id
            res['code'] = account.code
            res['name'] = account.name
            res['type'] = 'line'
            
            if account.id in account_result.keys():
                res['debit'] = account_result[account.id].get('debit')
                res['credit'] = account_result[account.id].get('credit')
                res['balance'] = account_result[account.id].get('balance')
            if account.id in account_result_previous.keys() and account.id in account_result.keys():
                res['balance_prev'] = account_result_previous[account.id].get('balance')
                res['balance_total'] = res['balance_prev'] + res['balance']
            elif account.id in account_result_previous.keys():
                res['debit'] = account_result_previous[account.id].get('debit')
                res['credit'] = account_result_previous[account.id].get('credit')
                res['balance'] = account_result_previous[account.id].get('balance')
                res['balance_prev'] = res['balance']
                res['balance_total'] = res['balance']
                
            def append_res():
                account_res.append(res)
                for partner_res in get_partners(account.id):
                    partner_res.update({'type': 'subline'})
                    account_res.append(partner_res)
                    
                res_subtotal = res.copy()
                res_subtotal['code'] = 'Subtotal'
                res_subtotal['type'] = 'subtotal'
                account_res.append(res_subtotal)
                
            if display_account == 'all':
                append_res()
            if display_account == 'not_zero' and not currency.is_zero(res['balance']):
                append_res()
            if display_account == 'movement' and (not currency.is_zero(res['debit']) or not currency.is_zero(res['credit'])):
                append_res()
                
        return account_res


    #tomado de: account/report/account_balance.py
    @api.model
    def render_html(self, docids, data=None):
        if not data.get('form') or not self.env.context.get('active_model'):
            raise UserError(_("Form content is missing, this report cannot be printed."))

        self.model = self.env.context.get('active_model')
        docs = self.env[self.model].browse(self.env.context.get('active_ids', []))
        display_account = data['form'].get('display_account')
        default_partner = data['form'].get('default_unknown_partner_id')
        accounts = docs if self.model == 'account.account' else self.env['account.account'].search([])
        account_res = self.with_context(data['form'].get('used_context'))._get_accounts(data['form'].get('used_context'), accounts, display_account, default_partner)

        docargs = {
            'doc_ids': self.ids,
            'doc_model': self.model,
            'data': data['form'],
            'docs': docs,
            'time': time,
            'Accounts': account_res,
        }

        return self.env['report'].render('anexo_al_balance.report_partner_trial_balance', docargs)
