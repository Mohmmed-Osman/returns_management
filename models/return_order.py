from odoo import models, fields, api, _
from odoo.exceptions import UserError


class ReturnOrder(models.Model):
    _name = 'return.order'
    _description = 'Return Order'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string='Reference',
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _('New')
    )
    type = fields.Selection([
        ('purchase', 'Purchase Return'),
        ('sale', 'Sales Return')],
        string='Type', default='sale', required=True)
    partner_id = fields.Many2one(
        'res.partner',
        string='Customer/Vendor',
        required=True)
    warehouse_id = fields.Many2one(
        'stock.warehouse',
        string='Warehouse',
        required=True)
    date = fields.Date(string='Return Date', default=fields.Date.context_today)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('delivered', 'Waiting Credit Note'),
        ('done', 'Done'),
        ('cancel', 'Cancelled')],
        string='Status', default='draft', tracking=True)
    line_ids = fields.One2many(
        'return.order.line',
        'return_id',
        string='Return Lines')
    origin = fields.Char(string='Source Document')
    picking_id = fields.Many2one('stock.picking', string='Related Picking')
    invoice_id = fields.Many2one('account.move', string='Related Invoice')
    credit_note_id = fields.Many2one('account.move', string='Credit Note')
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                if vals.get('type') == 'sale':
                    vals['name'] = self.env['ir.sequence'].next_by_code('return.sale.order') or _('New')
                else:
                    vals['name'] = self.env['ir.sequence'].next_by_code('return.purchase.order') or _('New')
        return super(ReturnOrder, self).create(vals_list)

    def action_confirm(self):
        for order in self:
            if not order.line_ids:
                raise UserError(_('You cannot confirm a return order without any lines.'))
            if self.type == 'sale':
                self._create_sale_return_picking()
            else:
                self._create_purchase_return_picking()
            order.state = 'confirmed'
        return True

    def action_cancel(self):
        for order in self:
            if order.picking_id and order.picking_id.state == 'done':
                raise UserError(_('You cannot cancel a return order if the related picking is done.'))
            order.state = 'cancel'
        return True

    def action_set_to_draft(self):
        """إعادة الأمر إلى حالة المسودة"""
        for order in self:
            if order.state != 'cancel':
                raise UserError(_("Can only reset canceled orders to draft."))

            # حذف المستندات المرتبطة إذا لزم الأمر
            if order.picking_id:
                order.picking_id.action_cancel()
                order.picking_id.unlink()

            if order.credit_note_id:
                order.credit_note_id.button_draft()
                order.credit_note_id.unlink()

            order.write({'state': 'draft'})
        return True

    def unlink(self):
        for order in self:
            if order.state not in ('draft', 'cancel'):
                raise UserError(_('You can only delete return orders in Draft or Cancelled state.'))
            if order.picking_id:
                raise UserError(_('You cannot delete a return order linked to a picking.'))
        return super(ReturnOrder, self).unlink()

    def action_done(self):
        print ('Done......')

