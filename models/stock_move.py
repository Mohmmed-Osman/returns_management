from odoo import models, fields, _
from odoo.exceptions import UserError


class StockMove(models.Model):
    _inherit = 'stock.move'

    return_line_id = fields.Many2one(
        'return.order.line',
        string='Return Order Line',
        ondelete='set null'
    )


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    return_id = fields.Many2one('return.order', string='Return Order')

    def write(self, vals):
        # res = super(StockPicking, self).write(vals)
        for rec in self:
            if vals.get('state') == 'done' or rec.state == 'done':
                rec.return_id.action_done()
                rec.return_id.line_ids['delivered_qty'] = 88
                print ("Printing From Write Method")
        # return res


class ReturnOrder(models.Model):
    _inherit = 'return.order'

    def _create_sale_return_picking(self):
        self.ensure_one()
        if not self.line_ids:
            raise UserError(_('Please specify return lines.'))
        if not self.company_id:
            raise UserError(_("Company is required for return operations!"))

        picking_type = self.env['stock.picking.type'].search([
            ('code', '=', 'incoming'),
            ('warehouse_id', '=', self.warehouse_id.id),
            ('company_id', '=', self.company_id.id),
        ], limit=1)

        if not picking_type:
            raise UserError(_('No return picking type found!'))

        picking_vals = {
            'company_id': self.company_id.id,
            'partner_id': self.partner_id.id,
            'picking_type_id': picking_type.id,
            'location_id': self.partner_id.property_stock_customer.id,
            'location_dest_id': picking_type.default_location_dest_id.id,
            'origin': self.name,
            'return_id': self.id,
        }
        picking = self.env['stock.picking'].create(picking_vals)

        for line in self.line_ids:
            move_vals = {
                'return_line_id': line.id,
                'name': line.product_id.name,
                'product_id': line.product_id.id,
                'product_uom_qty': line.quantity,
                'product_uom': line.product_id.uom_id.id,
                'picking_id': picking.id,
                'location_id': picking.location_id.id,
                'location_dest_id': picking.location_dest_id.id,
                'return_line_id': line.id,
                'company_id': self.company_id.id,
            }
            self.env['stock.move'].create(move_vals)

        self.picking_id = picking.id
        picking.action_confirm()
        picking.action_assign()
        return picking

    def _create_purchase_return_picking(self):
        self.ensure_one()
        if not self.line_ids:
            raise UserError(_('Please specify return lines.'))
        if not self.company_id:
            raise UserError(_("Company is required for return operations!"))

        picking_type = self.env['stock.picking.type'].search([
            ('code', '=', 'outgoing'),
            ('warehouse_id', '=', self.env.user._get_default_warehouse_id().id),
            ('company_id', '=', self.company_id.id),
        ], limit=1)

        if not picking_type:
            raise UserError(_('No return picking type found!'))

        picking_vals = {
            'company_id': self.company_id.id,
            'partner_id': self.partner_id.id,
            'picking_type_id': picking_type.id,
            'location_id': picking_type.default_location_src_id.id,
            'location_dest_id': self.partner_id.property_stock_supplier.id,
            'origin': self.name,
            'return_id': self.id,
        }
        picking = self.env['stock.picking'].create(picking_vals)

        for line in self.line_ids:
            move_vals = {
                'name': line.product_id.name,
                'product_id': line.product_id.id,
                'product_uom_qty': line.quantity,
                'product_uom': line.product_id.uom_id.id,
                'picking_id': picking.id,
                'location_id': picking.location_id.id,
                'location_dest_id': picking.location_dest_id.id,
                'return_line_id': line.id,
                'company_id': self.company_id.id,
            }
            self.env['stock.move'].create(move_vals)

        self.picking_id = picking.id
        picking.action_confirm()
        picking.action_assign()
        return picking

    def action_view_picking(self):
        self.ensure_one()
        if not self.picking_id:
            raise UserError(_('No picking found for this return.'))
        return {
            'name': _('Return Picking'),
            'view_mode': 'form',
            'res_model': 'stock.picking',
            'type': 'ir.actions.act_window',
            'res_id': self.picking_id.id,
            'target': 'current',
        }
