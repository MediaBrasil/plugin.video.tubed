# -*- coding: utf-8 -*-
"""
    Copyright (C) 2020 Tubed (plugin.video.tubed)

    This file is part of plugin.video.tubed

    SPDX-License-Identifier: GPL-2.0-only
    See LICENSES/GPL-2.0-only.txt for more information.
"""

import xbmcplugin  # pylint: disable=import-error

from ..constants import MODES
from ..generators.playlist import playlist_generator
from ..items.directory import Directory
from ..items.next_page import NextPage
from ..lib import txt_fmt
from ..lib.url_utils import create_addon_path


def invoke(context, channel_id, page_token=''):
    payload = context.api.channels(channel_id=channel_id)

    channel_item = payload.get('items', [{}])[0]
    content_details = channel_item.get('contentDetails', {})
    related_playlists = content_details.get('relatedPlaylists', {})
    upload_playlist = related_playlists.get('uploads', '')

    list_items = []

    if not page_token:
        if upload_playlist:
            directory = Directory(
                label=txt_fmt.bold(context.i18n('Uploads')),
                path=create_addon_path({
                    'mode': str(MODES.PLAYLIST),
                    'playlist_id': upload_playlist
                })
            )
            list_items.append(tuple(directory))

        if channel_id == 'mine':
            watch_later_playlist = ' ' + related_playlists.get('watchLater', '')

            if watch_later_playlist:
                directory = Directory(
                    label=txt_fmt.bold(context.i18n('Watch Later')),
                    path=create_addon_path({
                        'mode': str(MODES.PLAYLIST),
                        'playlist_id': watch_later_playlist
                    })
                )
                list_items.append(tuple(directory))

    payload = context.api.playlists_of_channel(channel_id=channel_id, page_token=page_token)
    list_items += list(playlist_generator(context, payload.get('items', [])))

    page_token = payload.get('nextPageToken')
    if page_token:
        directory = NextPage(
            label=context.i18n('Next Page'),
            path=create_addon_path({
                'mode': str(MODES.PLAYLISTS),
                'channel_id': channel_id,
                'page_token': page_token
            })
        )
        list_items.append(tuple(directory))

    xbmcplugin.addDirectoryItems(context.handle, list_items, len(list_items))

    xbmcplugin.endOfDirectory(context.handle, True)
