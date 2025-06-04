from odoo import models, fields, api, _
from odoo.exceptions import UserError


class ReturnAccountMove(models.Model):
    _inherit = 'account.move'

    return_order_id = fields.Many2one(
        'return.order',
        string='Related Return Order',
        ondelete='set null'
    )


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    return_line_id = fields.Many2one(
        'return.order.line',
        string='Return Order Line',
        ondelete='set null'
    )


class ReturnOrder(models.Model):
    _inherit = 'return.order'

    credit_note_id = fields.Many2one('account.move', string='Credit Note')

    def action_create_credit_note(self):
        """Create credit note from return order"""
        self.ensure_one()
        if self.credit_note_id:
            raise UserError(_('Credit Note already created.'))

        # تحديد نوع الفاتورة حسب نوع المرتجع
        move_type = 'out_refund' if self.type == 'sale' else 'in_refund'

        # تحضير بنود الفاتورة
        invoice_lines = []
        for line in self.line_ids:
            invoice_lines.append((0, 0, {
                'return_line_id': line.id,
                'product_id': line.product_id.id,
                'quantity': line.quantity,
                'price_unit': line.price_unit,
                'name': line.product_id.name,
                'tax_ids': [(6, 0, line.product_id.taxes_id.ids)],
            }))

        # إنشاء كريديت نوت
        credit_note = self.env['account.move'].create({
            'move_type': move_type,
            'partner_id': self.partner_id.id,
            'invoice_date': fields.Date.today(),
            'invoice_line_ids': invoice_lines,
            'return_order_id': self.id,
        })

        self.credit_note_id = credit_note.id

        # فتح الفاتورة للمستخدم
        return {
            'name': _('Credit Note'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'account.move',
            'res_id': credit_note.id,
        }

    def action_view_credit_note(self):
        self.ensure_one()
        if not self.credit_note_id:
            raise UserError(_('No Credit Note found for this return.'))

        return {
            'name': _('Credit Note'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'account.move',
            'res_id': self.credit_note_id.id,
            'target': 'current',

        }
