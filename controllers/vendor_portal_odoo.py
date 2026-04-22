# -*- coding: utf-8 -*-
#############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2025-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
#    Author: Cybrosys Techno Solutions(<https://www.cybrosys.com>)
#
#    You can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################
from collections import OrderedDict
from odoo import http, _
from odoo.exceptions import AccessError, ValidationError
from odoo.http import request
from odoo.addons.portal.controllers.portal import pager as portal_pager, \
    CustomerPortal


class RFQCustomerPortal(CustomerPortal):
    def _get_vendor_portal_domain(self):
        """Return the domain for RFQs visible to the current portal vendor."""
        partner = request.env.user.partner_id
        return [
            ('vendor_ids', 'in', partner.ids),
            ('state', 'not in', ['draft']),
        ]

    def _get_vendor_rfq_record(self, rfq_id):
        """Return a RFQ only when it belongs to the logged in vendor."""
        rfq = request.env['vendor.rfq'].sudo().browse(rfq_id)
        if not rfq.exists():
            raise AccessError(_("The requested RFQ does not exist."))
        partner = request.env.user.partner_id
        if partner not in rfq.vendor_ids:
            raise AccessError(_("You do not have access to this RFQ."))
        return rfq

    def _prepare_home_portal_values(self, counter):
        """Retrieves and prepares the values to be displayed on the home portal
        for the user."""
        values = super()._prepare_home_portal_values(counter)
        values['my_rfq_count'] = request.env['vendor.rfq'].sudo().search_count(
            self._get_vendor_portal_domain())
        return values

    def _rfq_get_page_view_values(self, vendor_rfq, access_token, **kwargs):
        """RFQ Page values"""
        values = {
            'page_name': 'vendor_rfq',
            'vendor_rfq': vendor_rfq,
        }
        return self._get_page_view_values(vendor_rfq, access_token, values,
                                          'my_rfq_history', False, **kwargs)

    @http.route(['/my/vendor_rfqs', '/my/vendor_rfqs/page/<int:page>'],
                type='http', auth="user", website=True)
    def portal_my_vendor_rfqs(self, page=1, date_begin=None,
                              date_end=None, sortby=None, filterby=None, **kw):
        """ Displays the portal page for vendor RFQs (Request for Quotations)
        for the logged-in user.This method is responsible for rendering the
        vendor RFQs in the portal with various filtering, sorting, and
        pagination options."""
        values = self._prepare_portal_layout_values()
        vendor_rfq = request.env['vendor.rfq'].sudo()
        domain = list(self._get_vendor_portal_domain())
        if date_begin and date_end:
            domain += [('create_date', '>', date_begin),
                       ('create_date', '<=', date_end)]

        searchbar_sortings = {
            'date': {'label': _('Newest'),
                     'order': 'create_date desc, id desc'},
            'name': {'label': _('Name'), 'order': 'name asc, id asc'},
        }
        if not sortby or sortby not in searchbar_sortings:
            sortby = 'name'
        order = searchbar_sortings[sortby]['order']
        searchbar_filters = {
            'all': {'label': _('All'), 'domain': [
                ('state', 'in', ['draft', 'in_progress', 'pending',
                                 'done', 'cancel'])]},
            'Done': {'label': _('Done'), 'domain': [('state', '=', 'done')]},
            'In Progress': {'label': _('In Progress'),
                            'domain': [('state', '=', 'in_progress')]},
        }
        # default filter by value
        if not filterby or filterby not in searchbar_filters:
            filterby = 'all'
        domain += searchbar_filters[filterby]['domain']
        rfq_unit_count = vendor_rfq.search_count(domain)
        pager = portal_pager(
            url="/my/vendor_rfqs",
            url_args={'date_begin': date_begin, 'date_end': date_end,
                      'sortby': sortby, 'filterby': filterby},
            total=rfq_unit_count,
            page=page,
            step=self._items_per_page
        )

        orders = vendor_rfq.search(
            domain,
            order=order,
            limit=self._items_per_page,
            offset=pager['offset']
        )
        values.update({
            'date': date_begin,
            'rfqs': orders,
            'page_name': 'vendor_rfq',
            'pager': pager,
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
            'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
            'filterby': filterby,
            'default_url': '/my/vendor_rfqs',
        })
        return request.render(
            "vendor_portal_odoo.portal_my_rfq",
            values)

    @http.route(['/my/vendor_rfq/<int:rfq_id>'], type='http', auth="user",
                website=True)
    def portal_my_vendor_rfq(self, rfq_id, access_token=None, **kw):
        """ Displays the details of a specific vendor RFQ (Request for Quotation)
         for the logged-in user."""
        rfq_details = self._get_vendor_rfq_record(int(rfq_id))
        vendor_quote = rfq_details.vendor_quote_history_ids.filtered(
            lambda x: x.vendor_id.id == request.env.user.partner_id.id
        )[:1]
        quoted_price = vendor_quote.quoted_price
        values = self._rfq_get_page_view_values(rfq_details, access_token, **kw)
        values['quoted_price'] = quoted_price
        values['vendor_quote'] = vendor_quote
        return request.render(
            "vendor_portal_odoo.portal_my_vendor_rfq", values)

    @http.route(['/quote/details'], type='http', auth="user", website=True,
                methods=['POST'])
    def quote_details(self, **post):
        """Handle the submission of a vendor's quote details."""
        try:
            rfq_id = int(post.get('rfq_id'))
            quoted_price = float(post.get('price'))
        except (TypeError, ValueError):
            raise ValidationError(_("Enter a valid quotation value."))
        if quoted_price <= 0:
            raise ValidationError(_("The quotation value must be greater than zero."))
        if not post.get('delivery_date'):
            raise ValidationError(_("Enter an estimated delivery date."))
        rfq = self._get_vendor_rfq_record(rfq_id)
        today = request.env.context_today(request.env.user)
        if rfq.state != 'in_progress':
            raise ValidationError(
                _("This RFQ is not accepting quotations anymore.")
            )
        if rfq.closing_date and rfq.closing_date < today:
            raise ValidationError(_("The quotation deadline has already passed."))
        vendor_quote = request.env['vendor.quote.history'].sudo().search([
            ('vendor_id', '=', request.env.user.partner_id.id),
            ('quote_id', '=', rfq.id),
        ], limit=1)
        values = {
            'vendor_id': request.env.user.partner_id.id,
            'quoted_price': quoted_price,
            'estimate_date': post.get('delivery_date'),
            'note': post.get('additional_note'),
            'quote_id': rfq.id,
        }
        if vendor_quote:
            vendor_quote.write(values)
        else:
            request.env['vendor.quote.history'].sudo().create(values)
        return request.redirect('/my/vendor_rfq/%s' % rfq.id)
