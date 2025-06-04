from odoo import models, fields, api


class ReturnOrderLine(models.Model):
    _name = 'return.order.line'
    _description = 'Return Order Line'

    delivered_qty = fields.Float(string="Delivered Quantity", compute='_compute_delivered_qty', store=True)
    invoiced_qty = fields.Float(string="Invoiced Quantity", compute='_compute_invoiced_qty', store=True)
    quantity = fields.Float(string='Quantity', default=1.0)
    price_unit = fields.Float(string='Unit Price', required=True)
    return_id = fields.Many2one('return.order', string='Return Order', ondelete='cascade')
    product_id = fields.Many2one('product.product', string='Product', required=True)
    move_id = fields.Many2one('stock.move', string='Stock Move')
    origin_sale_line_id = fields.Many2one('sale.order.line')
    origin_purchase_line_id = fields.Many2one('purchase.order.line')
    reason = fields.Selection([
        ('damaged', 'Damaged Product'),
        ('wrong', 'Wrong Product'),
        ('other', 'Other')], string='Return Reason')
    state = fields.Selection(related='return_id.state', string='Status', store=True)
    invoice_line_ids = fields.One2many('account.move.line', 'return_line_id', string='بنود الفواتير')

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.price_unit = self.product_id.standard_price

    def _compute_delivered_qty (self):
        for rec in self:
            rec.delivered_qty = 100

    def _compute_invoiced_qty (self):
        for rec in self:
            rec.invoiced_qty = 100

