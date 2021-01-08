# -*- coding: utf-8 -*-
import logging
import copy

from odoo import api, fields, models, exceptions, _
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.osv import expression
from odoo.tools import float_is_zero, float_compare
from itertools import groupby

_logger = logging.getLogger(__name__)

class account_custom_balance_in_group_0(models.Model):

    _inherit = 'account.financial.html.report.line'

    def _get_lines(self, financial_report, currency_table, options, linesDicts):
        final_result_table = []
        comparison_table = [options.get('date')]
        comparison_table += options.get('comparison') and options['comparison'].get('periods', []) or []
        currency_precision = self.env.company.currency_id.rounding

        # build comparison table
        for line in self:
            res = []
            debit_credit = len(comparison_table) == 1
            domain_ids = {'line'}
            k = 0

            for period in comparison_table:
                date_from = period.get('date_from', False)
                date_to = period.get('date_to', False) or period.get('date', False)
                date_from, date_to, strict_range = line.with_context(date_from=date_from, date_to=date_to)._compute_date_range()

                r = line.with_context(date_from=date_from,
                                      date_to=date_to,
                                      strict_range=strict_range)._eval_formula(financial_report,
                                                                               debit_credit,
                                                                               currency_table,
                                                                               linesDicts[k],
                                                                               groups=options.get('groups'))
                debit_credit = False
                res.extend(r)
                for column in r:
                    domain_ids.update(column)
                k += 1

            res = line._put_columns_together(res, domain_ids)

            if line.hide_if_zero and all([float_is_zero(k, precision_rounding=currency_precision) for k in res['line']]):
                continue

            # Post-processing ; creating line dictionnary, building comparison, computing total for extended, formatting
            vals = {
                'id': line.id,
                'name': line.name,
                'level': line.level,
                'class': 'o_account_reports_totals_below_sections' if self.env.company.totals_below_sections else '',
                'columns': [{'name': l} for l in res['line']],
                'unfoldable': len(domain_ids) > 1 and line.show_domain != 'always',
                'unfolded': line.id in options.get('unfolded_lines', []) or line.show_domain == 'always',
                'page_break': line.print_on_new_page,
            }

            if financial_report.tax_report and line.domain and not line.action_id:
                vals['caret_options'] = 'tax.report.line'

            if line.action_id:
                vals['action_id'] = line.action_id.id
            domain_ids.remove('line')
            lines = [vals]
            groupby = line.groupby or 'aml'
            if line.id in options.get('unfolded_lines', []) or line.show_domain == 'always':
                if line.groupby:
                    domain_ids = sorted(list(domain_ids), key=lambda k: line._get_gb_name(k))
                
                ##############################################################################
                if options.get('group_account_type', False) == True:
                    accounts = self.env['account.account'].search([('id','in',domain_ids)])
                    account_groups = []
                    for account in accounts:
                        exist_group = list(filter(lambda f:f['group_id'] == account.group_id.id, account_groups))
                        if(exist_group):
                            exist_group[0]['price'] = exist_group[0]['price'] + res[account.id][0]
                        else:
                            group_name = account.group_id.name_get()
                            if(group_name):
                                group_name = group_name[0]
                                account_groups.append({ 'group_id': account.group_id.id, 'name': group_name[1], 'price': res[account.id][0] })
                            else:
                                account_groups.append({ 'group_id': account.group_id.id, 'name': '', 'price': res[account.id][0] })

                    for account_group in account_groups:
                        name = account_group['name']
                        if not self.env.context.get('print_mode') or not self.env.context.get('no_format'):
                            name = name[:40] + '...' if name and len(name) >= 45 else name
                        vals = {
                            'id': account_group['group_id'],
                            'name': name,
                            'level': line.level,
                            'parent_id': line.id,
                            'columns': [{'name': account_group['price']}],
                            'caret_options': groupby == 'account_id' and 'account.account' or groupby,
                            'financial_group_line_id': line.id,
                            'custom_group': True,
                        }
                        if line.financial_report_id.name == 'Aged Receivable':
                            vals['trust'] = self.env['res.partner'].browse([account_group['group_id']]).trust
                        lines.append(vals)
                else:
                    for domain_id in domain_ids:
                        name = line._get_gb_name(domain_id)
                        if not self.env.context.get('print_mode') or not self.env.context.get('no_format'):
                            name = name[:40] + '...' if name and len(name) >= 45 else name
                        vals = {
                            'id': domain_id,
                            'name': name,
                            'level': line.level,
                            'parent_id': line.id,
                            'columns': [{'name': l} for l in res[domain_id]],
                            'caret_options': groupby == 'account_id' and 'account.account' or groupby,
                            'financial_group_line_id': line.id,
                        }
                        if line.financial_report_id.name == 'Aged Receivable':
                            vals['trust'] = self.env['res.partner'].browse([domain_id]).trust
                        lines.append(vals)
                ##############################################################################

                if domain_ids and self.env.company.totals_below_sections:
                    lines.append({
                        'id': 'total_' + str(line.id),
                        'name': _('Total') + ' ' + line.name,
                        'level': line.level,
                        'class': 'o_account_reports_domain_total',
                        'parent_id': line.id,
                        'columns': copy.deepcopy(lines[0]['columns']),
                    })

            for vals in lines:
                if len(comparison_table) == 2 and not options.get('groups'):
                    vals['columns'].append(line._build_cmp(vals['columns'][0]['name'], vals['columns'][1]['name']))
                    for i in [0, 1]:
                        vals['columns'][i] = line._format(vals['columns'][i])
                else:
                    vals['columns'] = [line._format(v) for v in vals['columns']]
                if not line.formulas:
                    vals['columns'] = [{'name': ''} for k in vals['columns']]
            
            if len(lines) == 1:
                new_lines = line.children_ids._get_lines(financial_report, currency_table, options, linesDicts)
                if new_lines and line.formulas:
                    if self.env.company.totals_below_sections:
                        divided_lines = self._divide_line(lines[0])
                        result = [divided_lines[0]] + new_lines + [divided_lines[-1]]
                    else:
                        result = [lines[0]] + new_lines
                else:
                    if not new_lines and not lines[0]['unfoldable'] and line.hide_if_empty:
                        lines = []
                    result = lines + new_lines
            else:
                result = lines
            final_result_table += result

        return final_result_table

    def _get_gb_name(self, gb_id):
        if self.groupby and self.env['account.move.line']._fields[self.groupby].relational:
            relation = self.env['account.move.line']._fields[self.groupby].comodel_name
            gb = self.env[relation].browse(gb_id)
            return gb.display_name if gb and gb.exists() else _('Undefined')
        return gb_id



class account_financial_html_report_custom(models.Model):
    
    _inherit = 'account.financial.html.report'

    group_account_type_filter = fields.Boolean('Group by account type')
    
    def _get_options(self, options):
        if(options != False and options.get("group_account_type", False)):
            self.filter_group_account_type = options['group_account_type']
        else:
            self.filter_group_account_type = False
        to_return = super(account_financial_html_report_custom, self)._get_options(options)
        return to_return

class AccountReportCustom(models.AbstractModel):
    
    _inherit = 'account.report'

    filter_group_account_type = None