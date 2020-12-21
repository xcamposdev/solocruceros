# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import base64
import logging

from odoo import http,tools, _
from odoo.http import request
from odoo.addons.base.models.assetsbundle import AssetsBundle

_logger = logging.getLogger(__name__)

class LivechatCustomController(http.Controller):

    # Note: the `cors` attribute on many routes is meant to allow the livechat
    # to be embedded in an external website.

    @http.route('/im_livechat/external_lib_sc.<any(css,js):ext>', type='http', auth='public')
    def livechat_lib(self, ext, **kwargs):
        # _get_asset return the bundle html code (script and link list) but we want to use the attachment content
        xmlid = 'im_livechat_custom_web.external_lib_witouth_custom'
        files, remains = request.env["ir.qweb"]._get_asset_content(xmlid, options=request.context)
        asset = AssetsBundle(xmlid, files)

        mock_attachment = getattr(asset, ext)()
        if isinstance(mock_attachment, list):  # suppose that CSS asset will not required to be split in pages
            mock_attachment = mock_attachment[0]
        # can't use /web/content directly because we don't have attachment ids (attachments must be created)
        status, headers, content = request.env['ir.http'].binary_content(id=mock_attachment.id, unique=asset.checksum)
        content_base64 = base64.b64decode(content) if content else ''
        headers.append(('Content-Length', len(content_base64)))
        return request.make_response(content_base64, headers)
