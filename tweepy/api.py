# Tweepy
# Copyright 2009-2010 Joshua Roesslein
# See LICENSE for details.

import os
import mimetypes
import urllib

from tweepy.binder import bind_api
from tweepy.error import TweepError
from tweepy.parsers import ModelParser, Parser
from tweepy.utils import list_to_csv


class API(object):
    """Twitter API"""

    def __init__(self, auth_handler=None,
                 host='api.twitter.com', search_host='search.twitter.com',
                 cache=None, api_root='/1.1', search_root='',
                 retry_count=0, retry_delay=0, retry_errors=None, timeout=60,
                 parser=None, compression=False, wait_on_rate_limit=False,
                 wait_on_rate_limit_notify=False, proxy=''):
        """ Api instance Constructor

        :param auth_handler:
        :param host:  url of the server of the rest api, default:'api.twitter.com'
        :param search_host: url of the search server, default:'search.twitter.com'
        :param cache: Cache to query if a GET method is used, default:None
        :param api_root: suffix of the api version, default:'/1.1'
        :param search_root: suffix of the search version, default:''
        :param retry_count: number of allowed retries, default:0
        :param retry_delay: delay in second between retries, default:0
        :param retry_errors: default:None
        :param timeout: delay before to consider the request as timed out in seconds, default:60
        :param parser: ModelParser instance to parse the responses, default:None
        :param compression: If the response is compressed, default:False
        :param wait_on_rate_limit: If the api wait when it hits the rate limit, default:False
        :param wait_on_rate_limit_notify: If the api print a notification when the rate limit is hit, default:False
        :param proxy: Url to use as proxy during the HTTP request, default:''

        :raise TypeError: If the given parser is not a ModelParser instance.
        """
        self.auth = auth_handler
        self.host = host
        self.search_host = search_host
        self.api_root = api_root
        self.search_root = search_root
        self.cache = cache
        self.compression = compression
        self.retry_count = retry_count
        self.retry_delay = retry_delay
        self.retry_errors = retry_errors
        self.timeout = timeout
        self.wait_on_rate_limit = wait_on_rate_limit
        self.wait_on_rate_limit_notify = wait_on_rate_limit_notify
        self.parser = parser or ModelParser()
        self.proxy = {}
        if proxy:
            self.proxy['https'] = proxy

        # Attempt to explain more clearly the parser argument requirements
        # https://github.com/tweepy/tweepy/issues/421
        #
        parser_type = Parser
        if not isinstance(self.parser, parser_type):
            raise TypeError(
                '"parser" argument has to be an instance of "{}". It is currently a {}.'.format(
                    parser_type.__name__, type(self.parser)
                )
            )

    @property
    def home_timeline(self):
        """ :reference: https://dev.twitter.com/docs/api/1.1/get/statuses/home_timeline
            :allowed_param:'since_id', 'max_id', 'count'
        """
        return bind_api(
            api=self,
            path='/statuses/home_timeline.json',
            payload_type='status', payload_list=True,
            allowed_param=['since_id', 'max_id', 'count'],
            require_auth=True
        )

    def statuses_lookup(self, id_, include_entities=None, trim_user=None, map_=None):
        return self._statuses_lookup(list_to_csv(id_), include_entities,
                                     trim_user, map_)

    @property
    def _statuses_lookup(self):
        """ :reference: https://dev.twitter.com/docs/api/1.5/get/statuses/lookup
            :allowed_param:'id', 'include_entities', 'trim_user', 'map'
        """
        return bind_api(
            api=self,
            path='/statuses/lookup.json',
            payload_type='status', payload_list=True,
            allowed_param=['id', 'include_entities', 'trim_user', 'map'],
            require_auth=True
        )

    @property
    def user_timeline(self):
        """ :reference: https://dev.twitter.com/docs/api/1.1/get/statuses/user_timeline
            :allowed_param:'id', 'user_id', 'screen_name', 'since_id'
        """
        return bind_api(
            api=self,
            path='/statuses/user_timeline.json',
            payload_type='status', payload_list=True,
            allowed_param=['id', 'user_id', 'screen_name', 'since_id',
                           'max_id', 'count', 'include_rts']
        )

    @property
    def mentions_timeline(self):
        """ :reference: https://dev.twitter.com/docs/api/1.1/get/statuses/mentions_timeline
            :allowed_param:'since_id', 'max_id', 'count'
        """
        return bind_api(
            api=self,
            path='/statuses/mentions_timeline.json',
            payload_type='status', payload_list=True,
            allowed_param=['since_id', 'max_id', 'count'],
            require_auth=True
        )

    @property
    def related_results(self):
        """ :reference: https://dev.twitter.com/docs/api/1.1/get/related_results/show/%3id.format
            :allowed_param:'id'
        """
        return bind_api(
            api=self,
            path='/related_results/show/{id}.json',
            payload_type='relation', payload_list=True,
            allowed_param=['id'],
            require_auth=False
        )

    @property
    def retweets_of_me(self):
        """ :reference: https://dev.twitter.com/docs/api/1.1/get/statuses/retweets_of_me
            :allowed_param:'since_id', 'max_id', 'count'
        """
        return bind_api(
            api=self,
            path='/statuses/retweets_of_me.json',
            payload_type='status', payload_list=True,
            allowed_param=['since_id', 'max_id', 'count'],
            require_auth=True
        )

    @property
    def get_status(self):
        """ :reference: https://dev.twitter.com/docs/api/1.1/get/statuses/show
            :allowed_param:'id
        """
        return bind_api(
            api=self,
            path='/statuses/show.json',
            payload_type='status',
            allowed_param=['id']
        )


    @property
    def update_status(self):
        """ :reference: https://dev.twitter.com/docs/api/1.1/post/statuses/update
            :allowed_param:'status', 'in_reply_to_status_id', 'lat', 'long', 'source', 'place_id', 'display_coordinates'
        """
        return bind_api(
            api=self,
            path='/statuses/update.json',
            method='POST',
            payload_type='status',
            allowed_param=['status', 'in_reply_to_status_id', 'lat', 'long', 'source', 'place_id', 'display_coordinates'],
            require_auth=True
        )

    def update_with_media(self, filename, *args, **kwargs):
        """ :reference: https://dev.twitter.com/docs/api/1.1/post/statuses/update_with_media """
        f = kwargs.pop('file', None)
        headers, post_data = API._pack_image(filename, 3072, form_field='media[]', f=f)
        kwargs.update({'headers': headers, 'post_data': post_data})

        return bind_api(
            api=self,
            path='/statuses/update_with_media.json',
            method='POST',
            payload_type='status',
            allowed_param=[
                'status', 'possibly_sensitive', 'in_reply_to_status_id', 'lat', 'long',
                'place_id', 'display_coordinates'
            ],
            require_auth=True
        )(*args, **kwargs)

    @property
    def destroy_status(self):
        """ :reference: https://dev.twitter.com/docs/api/1.1/post/statuses/destroy
            :allowed_param:'id'
        """
        return bind_api(
            api=self,
            path='/statuses/destroy/{id}.json',
            method='POST',
            payload_type='status',
            allowed_param=['id'],
            require_auth=True
        )

    @property
    def retweet(self):
        """ :reference: https://dev.twitter.com/docs/api/1.1/post/statuses/retweet
            :allowed_param:'id'
        """
        return bind_api(
            api=self,
            path='/statuses/retweet/{id}.json',
            method='POST',
            payload_type='status',
            allowed_param=['id'],
            require_auth=True
        )

    @property
    def retweets(self):
        """ :reference: https://dev.twitter.com/docs/api/1.1/get/statuses/retweets
            :allowed_param:'id', 'count'
        """
        return bind_api(
            api=self,
            path='/statuses/retweets/{id}.json',
            payload_type='status', payload_list=True,
            allowed_param=['id', 'count'],
            require_auth=True
        )

    @property
    def retweeters(self):
        """ 
            :allowed_param:'id', 'cursor', 'stringify_ids
        """
        return bind_api(
            api=self,
            path='/statuses/retweeters/ids.json',
            payload_type='ids',
            allowed_param=['id', 'cursor', 'stringify_ids']
        )

    @property
    def get_user(self):
        """ :reference: https://dev.twitter.com/docs/api/1.1/get/users/show
            :allowed_param:'id', 'user_id', 'screen_name
        """
        return bind_api(
            api=self,
            path='/users/show.json',
            payload_type='user',
            allowed_param=['id', 'user_id', 'screen_name']
        )

    @property
    def get_oembed(self):
        """ :reference: https://dev.twitter.com/docs/api/1.1/get/statuses/oembed
            :allowed_param:'id', 'url', 'maxwidth', 'hide_media', 'omit_script', 'align', 'related', 'lang
        """
        return bind_api(
            api=self,
            path='/statuses/oembed.json',
            payload_type='json',
            allowed_param=['id', 'url', 'maxwidth', 'hide_media', 'omit_script', 'align', 'related', 'lang']
        )

    def lookup_users(self, user_ids=None, screen_names=None):
        """ Perform bulk look up of users from user ID or screenname """
        return self._lookup_users(list_to_csv(user_ids), list_to_csv(screen_names))

    @property
    def _lookup_users(self):
        """ :reference: https://dev.twitter.com/docs/api/1.1/get/users/lookup.json
            allowed_param=['user_id', 'screen_name'],
        """
        return bind_api(
            api=self,
            path='/users/lookup.json',
            payload_type='user', payload_list=True,
            allowed_param=['user_id', 'screen_name'],
        )

    def me(self):
        """ Get the authenticated user """
        return self.get_user(screen_name=self.auth.get_username())

    @property
    def search_users(self):
        """ :reference: https://dev.twitter.com/docs/api/1.1/get/users/search
            :allowed_param:'q', 'count', 'page'
        """
        return bind_api(
            api=self,
            path='/users/search.json',
            payload_type='user', payload_list=True,
            require_auth=True,
            allowed_param=['q', 'count', 'page']
        )

    @property
    def suggested_users(self):
        """ :reference: https://dev.twitter.com/docs/api/1.1/get/users/suggestions/%3slug
            :allowed_param:'slug', 'lang
        """
        return bind_api(
            api=self,
            path='/users/suggestions/{slug}.json',
            payload_type='user', payload_list=True,
            require_auth=True,
            allowed_param=['slug', 'lang']
        )

    @property
    def suggested_categories(self):
        """ :reference: https://dev.twitter.com/docs/api/1.1/get/users/suggestions
            :allowed_param:'lang'
        """
        return bind_api(
            api=self,
            path='/users/suggestions.json',
            payload_type='category', payload_list=True,
            allowed_param=['lang'],
            require_auth=True
        )

    @property
    def suggested_users_tweets(self):
        """ :reference: https://dev.twitter.com/docs/api/1.1/get/users/suggestions/%3slug/members
            :allowed_param:'slug'
        """
        return bind_api(
            api=self,
            path='/users/suggestions/{slug}/members.json',
            payload_type='status', payload_list=True,
            allowed_param=['slug'],
            require_auth=True
        )

    @property
    def direct_messages(self):
        """ :reference: https://dev.twitter.com/docs/api/1.1/get/direct_messages
            :allowed_param:'since_id', 'max_id', 'count'
        """
        return bind_api(
            api=self,
            path='/direct_messages.json',
            payload_type='direct_message', payload_list=True,
            allowed_param=['since_id', 'max_id', 'count'],
            require_auth=True
        )

    @property
    def get_direct_message(self):
        """ :reference: https://dev.twitter.com/docs/api/1.1/get/direct_messages/show
            :allowed_param:'id'
        """
        return bind_api(
            api=self,
            path='/direct_messages/show/{id}.json',
            payload_type='direct_message',
            allowed_param=['id'],
            require_auth=True
        )

    @property
    def sent_direct_messages(self):
        """ :reference: https://dev.twitter.com/docs/api/1.1/get/direct_messages/sent
            :allowed_param:'since_id', 'max_id', 'count', 'page'
        """
        return bind_api(
            api=self,
            path='/direct_messages/sent.json',
            payload_type='direct_message', payload_list=True,
            allowed_param=['since_id', 'max_id', 'count', 'page'],
            require_auth=True
        )

    @property
    def send_direct_message(self):
        """ :reference: https://dev.twitter.com/docs/api/1.1/post/direct_messages/new
            :allowed_param:'user', 'screen_name', 'user_id', 'text'
        """
        return bind_api(
            api=self,
            path='/direct_messages/new.json',
            method='POST',
            payload_type='direct_message',
            allowed_param=['user', 'screen_name', 'user_id', 'text'],
            require_auth=True
        )

    @property
    def destroy_direct_message(self):
        """ :reference: https://dev.twitter.com/docs/api/1.1/delete/direct_messages/destroy
            :allowed_param:'id'
        """
        return bind_api(
            api=self,
            path='/direct_messages/destroy.json',
            method='DELETE',
            payload_type='direct_message',
            allowed_param=['id'],
            require_auth=True
        )

    @property
    def create_friendship(self):
        """ :reference: https://dev.twitter.com/docs/api/1.1/post/friendships/create
            :allowed_param:'id', 'user_id', 'screen_name', 'follow'
        """
        return bind_api(
            api=self,
            path='/friendships/create.json',
            method='POST',
            payload_type='user',
            allowed_param=['id', 'user_id', 'screen_name', 'follow'],
            require_auth=True
        )

    @property
    def destroy_friendship(self):
        """ :reference: https://dev.twitter.com/docs/api/1.1/delete/friendships/destroy
            :allowed_param:'id', 'user_id', 'screen_name'
        """
        return bind_api(
            api=self,
            path='/friendships/destroy.json',
            method='DELETE',
            payload_type='user',
            allowed_param=['id', 'user_id', 'screen_name'],
            require_auth=True
        )

    @property
    def show_friendship(self):
        """ :reference: https://dev.twitter.com/docs/api/1.1/get/friendships/show
            :allowed_param:'source_id', 'source_screen_name',
        """
        return bind_api(
            api=self,
            path='/friendships/show.json',
            payload_type='friendship',
            allowed_param=['source_id', 'source_screen_name',
                           'target_id', 'target_screen_name']
        )

    def lookup_friendships(self, user_ids=None, screen_names=None):
        """ Perform bulk look up of friendships from user ID or screenname """
        return self._lookup_friendships(list_to_csv(user_ids), list_to_csv(screen_names))

    @property
    def _lookup_friendships(self):
        """ :reference: https://dev.twitter.com/docs/api/1.1/get/friendships/lookup
            :allowed_param:'user_id', 'screen_name'
        """
        return bind_api(
            api=self,
            path='/friendships/lookup.json',
            payload_type='relationship', payload_list=True,
            allowed_param=['user_id', 'screen_name'],
            require_auth=True
        )

    @property
    def friends_ids(self):
        """ :reference: https://dev.twitter.com/docs/api/1.1/get/friends/ids
            :allowed_param:'id', 'user_id', 'screen_name', 'cursor
        """
        return bind_api(
            api=self,
            path='/friends/ids.json',
            payload_type='ids',
            allowed_param=['id', 'user_id', 'screen_name', 'cursor']
        )

    @property
    def friends(self):
        """ :reference: https://dev.twitter.com/docs/api/1.1/get/friends/list
            :allowed_param:'id', 'user_id', 'screen_name', 'cursor
        """
        return bind_api(
            api=self,
            path='/friends/list.json',
            payload_type='user', payload_list=True,
            allowed_param=['id', 'user_id', 'screen_name', 'cursor']
        )

    @property
    def friendships_incoming(self):
        """ :reference: https://dev.twitter.com/docs/api/1.1/get/friendships/incoming
            :allowed_param:'cursor
        """
        return bind_api(
            api=self,
            path='/friendships/incoming.json',
            payload_type='ids',
            allowed_param=['cursor']
        )

    @property
    def friendships_outgoing(self):
        """ :reference: https://dev.twitter.com/docs/api/1.1/get/friendships/outgoing
            :allowed_param:'cursor
        """
        return bind_api(
            api=self,
            path='/friendships/outgoing.json',
            payload_type='ids',
            allowed_param=['cursor']
        )

    @property
    def followers_ids(self):
        """ :reference: https://dev.twitter.com/docs/api/1.1/get/followers/ids
            :allowed_param:'id', 'user_id', 'screen_name', 'cursor', 'count
        """
        return bind_api(
            api=self,
            path='/followers/ids.json',
            payload_type='ids',
            allowed_param=['id', 'user_id', 'screen_name', 'cursor', 'count']
        )

    @property
    def followers(self):
        """ :reference: https://dev.twitter.com/docs/api/1.1/get/followers/list
            :allowed_param:'id', 'user_id', 'screen_name', 'cursor', 'count', 'skip_status', 'include_user_entities'
        """
        return bind_api(
            api=self,
            path='/followers/list.json',
            payload_type='user', payload_list=True,
            allowed_param=['id', 'user_id', 'screen_name', 'cursor', 'count',
                           'skip_status', 'include_user_entities']
        )

    def verify_credentials(self, **kargs):
        """ account/verify_credentials """
        try:
            return bind_api(
                api=self,
                path='/account/verify_credentials.json',
                payload_type='user',
                require_auth=True,
                allowed_param=['include_entities', 'skip_status'],
            )(**kargs)
        except TweepError as e:
            if e.response and e.response.status == 401:
                return False
            raise

    @property
    def rate_limit_status(self):
        """ :reference: https://dev.twitter.com/docs/api/1.1/get/account/rate_limit_status
            :allowed_param:'resources'
        """
        return bind_api(
            api=self,
            path='/application/rate_limit_status.json',
            payload_type='json',
            allowed_param=['resources'],
            use_cache=False
        )

    @property
    def set_delivery_device(self):
        """ :reference: https://dev.twitter.com/docs/api/1.1/post/account/update_delivery_device
            :allowed_param:'device'
        """
        return bind_api(
            api=self,
            path='/account/update_delivery_device.json',
            method='POST',
            allowed_param=['device'],
            payload_type='user',
            require_auth=True
        )

    @property
    def update_profile_colors(self):
        """ :reference: https://dev.twitter.com/docs/api/1.1/post/account/update_profile_colors
            :allowed_param:'profile_background_color', 'profile_text_color', 'profile_link_color', 'profile_sidebar_fill_color', 'profile_sidebar_border_color'],
        """
        return bind_api(
            api=self,
            path='/account/update_profile_colors.json',
            method='POST',
            payload_type='user',
            allowed_param=['profile_background_color', 'profile_text_color',
                           'profile_link_color', 'profile_sidebar_fill_color',
                           'profile_sidebar_border_color'],
            require_auth=True
        )

    def update_profile_image(self, filename, file_=None):
        """ :reference: https://dev.twitter.com/docs/api/1.1/post/account/update_profile_image """
        headers, post_data = API._pack_image(filename, 700, f=file_)
        return bind_api(
            api=self,
            path='/account/update_profile_image.json',
            method='POST',
            payload_type='user',
            require_auth=True
        )(self, post_data=post_data, headers=headers)

    def update_profile_background_image(self, filename, **kargs):
        """ :reference: https://dev.twitter.com/docs/api/1.1/post/account/update_profile_background_image """
        f = kargs.pop('file', None)
        headers, post_data = API._pack_image(filename, 800, f=f)
        bind_api(
            api=self,
            path='/account/update_profile_background_image.json',
            method='POST',
            payload_type='user',
            allowed_param=['tile', 'include_entities', 'skip_status', 'use'],
            require_auth=True
        )(self, post_data=post_data, headers=headers)

    def update_profile_banner(self, filename, **kargs):
        """ :reference: https://dev.twitter.com/docs/api/1.1/post/account/update_profile_banner """
        f = kargs.pop('file', None)
        headers, post_data = API._pack_image(filename, 700, form_field="banner", f=f)
        bind_api(
            api=self,
            path='/account/update_profile_banner.json',
            method='POST',
            allowed_param=['width', 'height', 'offset_left', 'offset_right'],
            require_auth=True
        )(self, post_data=post_data, headers=headers)

    @property
    def update_profile(self):
        """ :reference: https://dev.twitter.com/docs/api/1.1/post/account/update_profile
            :allowed_param:'name', 'url', 'location', 'description'
        """
        return bind_api(
            api=self,
            path='/account/update_profile.json',
            method='POST',
            payload_type='user',
            allowed_param=['name', 'url', 'location', 'description'],
            require_auth=True
        )

    @property
    def favorites(self):
        """ :reference: https://dev.twitter.com/docs/api/1.1/get/favorites
            :allowed_param:'screen_name', 'user_id', 'max_id', 'count', 'since_id', 'max_id
        """
        return bind_api(
            api=self,
            path='/favorites/list.json',
            payload_type='status', payload_list=True,
            allowed_param=['screen_name', 'user_id', 'max_id', 'count', 'since_id', 'max_id']
        )

    @property
    def create_favorite(self):
        """ :reference: https://dev.twitter.com/docs/api/1.1/post/favorites/create
            :allowed_param:'id'
        """
        return bind_api(
            api=self,
            path='/favorites/create.json',
            method='POST',
            payload_type='status',
            allowed_param=['id'],
            require_auth=True
        )

    @property
    def destroy_favorite(self):
        """ :reference: https://dev.twitter.com/docs/api/1.1/post/favorites/destroy
            :allowed_param:'id'
        """
        return bind_api(
            api=self,
            path='/favorites/destroy.json',
            method='POST',
            payload_type='status',
            allowed_param=['id'],
            require_auth=True
        )

    @property
    def create_block(self):
        """ :reference: https://dev.twitter.com/docs/api/1.1/post/blocks/create
            :allowed_param:'id', 'user_id', 'screen_name'
        """
        return bind_api(
            api=self,
            path='/blocks/create.json',
            method='POST',
            payload_type='user',
            allowed_param=['id', 'user_id', 'screen_name'],
            require_auth=True
        )

    @property
    def destroy_block(self):
        """ :reference: https://dev.twitter.com/docs/api/1.1/delete/blocks/destroy
            :allowed_param:'id', 'user_id', 'screen_name'
        """
        return bind_api(
            api=self,
            path='/blocks/destroy.json',
            method='DELETE',
            payload_type='user',
            allowed_param=['id', 'user_id', 'screen_name'],
            require_auth=True
        )

    @property
    def blocks(self):
        """ :reference: https://dev.twitter.com/docs/api/1.1/get/blocks/blocking
            :allowed_param:'cursor'
        """
        return bind_api(
            api=self,
            path='/blocks/list.json',
            payload_type='user', payload_list=True,
            allowed_param=['cursor'],
            require_auth=True
        )

    @property
    def blocks_ids(self):
        """ :reference: https://dev.twitter.com/docs/api/1.1/get/blocks/ids """
        return bind_api(
            api=self,
            path='/blocks/ids.json',
            payload_type='json',
            require_auth=True
        )

    @property
    def report_spam(self):
        """ :reference: https://dev.twitter.com/docs/api/1.1/post/report_spam
            :allowed_param:'user_id', 'screen_name'
        """
        return bind_api(
            api=self,
            path='/users/report_spam.json',
            method='POST',
            payload_type='user',
            allowed_param=['user_id', 'screen_name'],
            require_auth=True
        )

    @property
    def saved_searches(self):
        """ :reference: https://dev.twitter.com/docs/api/1.1/get/saved_searches/show/%3Aid """
        return bind_api(
            api=self,
            path='/saved_searches/list.json',
            payload_type='saved_search', payload_list=True,
            require_auth=True
        )

    @property
    def get_saved_search(self):
        """ :reference: https://dev.twitter.com/docs/api/1.1/get/saved_searches/show/%3Aid
            :allowed_param:'id'
        """
        return bind_api(
            api=self,
            path='/saved_searches/show/{id}.json',
            payload_type='saved_search',
            allowed_param=['id'],
            require_auth=True
        )

    @property
    def create_saved_search(self):
        """ :reference: https://dev.twitter.com/docs/api/1.1/post/saved_searches/create
            :allowed_param:'query'
        """
        return bind_api(
            api=self,
            path='/saved_searches/create.json',
            method='POST',
            payload_type='saved_search',
            allowed_param=['query'],
            require_auth=True
        )

    @property
    def destroy_saved_search(self):
        """ :reference: https://dev.twitter.com/docs/api/1.1/post/saved_searches/destroy
            :allowed_param:'id'
        """
        return bind_api(
            api=self,
            path='/saved_searches/destroy/{id}.json',
            method='POST',
            payload_type='saved_search',
            allowed_param=['id'],
            require_auth=True
        )

    @property
    def create_list(self):
        """ :reference: https://dev.twitter.com/docs/api/1.1/post/lists/create
            :allowed_param:'name', 'mode', 'description'
        """
        return bind_api(
            api=self,
            path='/lists/create.json',
            method='POST',
            payload_type='list',
            allowed_param=['name', 'mode', 'description'],
            require_auth=True
        )

    @property
    def destroy_list(self):
        """ :reference: https://dev.twitter.com/docs/api/1.1/post/lists/destroy
            :allowed_param:'owner_screen_name', 'owner_id', 'list_id', 'slug'
        """
        return bind_api(
            api=self,
            path='/lists/destroy.json',
            method='POST',
            payload_type='list',
            allowed_param=['owner_screen_name', 'owner_id', 'list_id', 'slug'],
            require_auth=True
        )

    @property
    def update_list(self):
        """ :reference: https://dev.twitter.com/docs/api/1.1/post/lists/update
            :allowed_param: list_id', 'slug', 'name', 'mode', 'description', 'owner_screen_name', 'owner_id'
        """
        return bind_api(
            api=self,
            path='/lists/update.json',
            method='POST',
            payload_type='list',
            allowed_param=['list_id', 'slug', 'name', 'mode', 'description', 'owner_screen_name', 'owner_id'],
            require_auth=True
        )

    @property
    def lists_all(self):
        """ :reference: https://dev.twitter.com/docs/api/1.1/get/lists/list
            :allowed_param:'screen_name', 'user_id'
        """
        return bind_api(
            api=self,
            path='/lists/list.json',
            payload_type='list', payload_list=True,
            allowed_param=['screen_name', 'user_id'],
            require_auth=True
        )

    @property
    def lists_memberships(self):
        """ :reference: https://dev.twitter.com/docs/api/1.1/get/lists/memberships
            :allowed_param:'screen_name', 'user_id', 'filter_to_owned_lists', 'cursor'
        """
        return bind_api(
            api=self,
            path='/lists/memberships.json',
            payload_type='list', payload_list=True,
            allowed_param=['screen_name', 'user_id', 'filter_to_owned_lists', 'cursor'],
            require_auth=True
        )

    @property
    def lists_subscriptions(self):
        """ :reference: https://dev.twitter.com/docs/api/1.1/get/lists/subscriptions
            :allowed_param:'screen_name', 'user_id', 'cursor'
        """
        return bind_api(
            api=self,
            path='/lists/subscriptions.json',
            payload_type='list', payload_list=True,
            allowed_param=['screen_name', 'user_id', 'cursor'],
            require_auth=True
        )

    @property
    def list_timeline(self):
        """ :reference: https://dev.twitter.com/docs/api/1.1/get/lists/statuses
            :allowed_param:'owner_screen_name', 'slug', 'owner_id', 'list_id', 'since_id', 'max_id', 'count', 'include_rts
        """
        return bind_api(
            api=self,
            path='/lists/statuses.json',
            payload_type='status', payload_list=True,
            allowed_param=['owner_screen_name', 'slug', 'owner_id', 'list_id', 'since_id', 'max_id', 'count', 'include_rts']
        )

    @property
    def get_list(self):
        """ :reference: https://dev.twitter.com/docs/api/1.1/get/lists/show
            :allowed_param:'owner_screen_name', 'owner_id', 'slug', 'list_id
        """
        return bind_api(
            api=self,
            path='/lists/show.json',
            payload_type='list',
            allowed_param=['owner_screen_name', 'owner_id', 'slug', 'list_id']
        )

    @property
    def add_list_member(self):
        """ :reference: https://dev.twitter.com/docs/api/1.1/post/lists/members/create
            :allowed_param:'screen_name', 'user_id', 'owner_screen_name', 'owner_id', 'slug', 'list_id'
        """
        return bind_api(
            api=self,
            path='/lists/members/create.json',
            method='POST',
            payload_type='list',
            allowed_param=['screen_name', 'user_id', 'owner_screen_name', 'owner_id', 'slug', 'list_id'],
            require_auth=True
        )

    @property
    def remove_list_member(self):
        """ :reference: https://dev.twitter.com/docs/api/1.1/post/lists/members/destroy
            :allowed_param:'screen_name', 'user_id', 'owner_screen_name', 'owner_id', 'slug', 'list_id'
        """
        return bind_api(
            api=self,
            path='/lists/members/destroy.json',
            method='POST',
            payload_type='list',
            allowed_param=['screen_name', 'user_id', 'owner_screen_name', 'owner_id', 'slug', 'list_id'],
            require_auth=True
        )

    def add_list_members(self, screen_name=None, user_id=None, slug=None,
                         list_id=None, owner_id=None, owner_screen_name=None):
        """ Perform bulk add of list members from user ID or screenname """
        return self._add_list_members(list_to_csv(screen_name),
                                      list_to_csv(user_id),
                                      slug, list_id, owner_id,
                                      owner_screen_name)

    @property
    def _add_list_members(self):
        """ :reference: https://dev.twitter.com/docs/api/1.1/post/lists/members/create_all
            :allowed_param:'screen_name', 'user_id', 'slug', 'lit_id', 'owner_id', 'owner_screen_name'
        """
        return bind_api(
            api=self,
            path='/lists/members/create_all.json',
            method='POST',
            payload_type='list',
            allowed_param=['screen_name', 'user_id', 'slug', 'lit_id', 'owner_id', 'owner_screen_name'],
            require_auth=True
        )


    def remove_list_members(self, screen_name=None, user_id=None, slug=None,
                            list_id=None, owner_id=None, owner_screen_name=None):
        """ Perform bulk remove of list members from user ID or screenname """
        return self._remove_list_members(list_to_csv(screen_name),
                                         list_to_csv(user_id),
                                         slug, list_id, owner_id,
                                         owner_screen_name)

    @property
    def _remove_list_members(self):
        """ :reference: https://dev.twitter.com/docs/api/1.1/post/lists/members/destroy_all
            :allowed_param:'screen_name', 'user_id', 'slug', 'lit_id', 'owner_id', 'owner_screen_name'
        """
        return bind_api(
            api=self,
            path='/lists/members/destroy_all.json',
            method='POST',
            payload_type='list',
            allowed_param=['screen_name', 'user_id', 'slug', 'lit_id', 'owner_id', 'owner_screen_name'],
            require_auth=True
        )

    @property
    def list_members(self):
        """ :reference: https://dev.twitter.com/docs/api/1.1/get/lists/members
            :allowed_param:'owner_screen_name', 'slug', 'list_id', 'owner_id', 'cursor
        """
        return bind_api(
            api=self,
            path='/lists/members.json',
            payload_type='user', payload_list=True,
            allowed_param=['owner_screen_name', 'slug', 'list_id', 'owner_id', 'cursor']
        )

    @property
    def show_list_member(self):
        """ :reference: https://dev.twitter.com/docs/api/1.1/get/lists/members/show
            :allowed_param:'list_id', 'slug', 'user_id', 'screen_name', 'owner_screen_name', 'owner_id
        """
        return bind_api(
            api=self,
            path='/lists/members/show.json',
            payload_type='user',
            allowed_param=['list_id', 'slug', 'user_id', 'screen_name', 'owner_screen_name', 'owner_id']
        )

    @property
    def subscribe_list(self):
        """ :reference: https://dev.twitter.com/docs/api/1.1/post/lists/subscribers/create
            :allowed_param:'owner_screen_name', 'slug', 'owner_id', 'list_id'
        """
        return bind_api(
            api=self,
            path='/lists/subscribers/create.json',
            method='POST',
            payload_type='list',
            allowed_param=['owner_screen_name', 'slug', 'owner_id', 'list_id'],
            require_auth=True
        )

    @property
    def unsubscribe_list(self):
        """ :reference: https://dev.twitter.com/docs/api/1.1/post/lists/subscribers/destroy
            :allowed_param:'owner_screen_name', 'slug', 'owner_id', 'list_id'
        """
        return bind_api(
            api=self,
            path='/lists/subscribers/destroy.json',
            method='POST',
            payload_type='list',
            allowed_param=['owner_screen_name', 'slug', 'owner_id', 'list_id'],
            require_auth=True
        )

    @property
    def list_subscribers(self):
        """ :reference: https://dev.twitter.com/docs/api/1.1/get/lists/subscribers
            :allowed_param:'owner_screen_name', 'slug', 'owner_id', 'list_id', 'cursor
        """
        return bind_api(
            api=self,
            path='/lists/subscribers.json',
            payload_type='user', payload_list=True,
            allowed_param=['owner_screen_name', 'slug', 'owner_id', 'list_id', 'cursor']
        )

    @property
    def show_list_subscriber(self):
        """ :reference: https://dev.twitter.com/docs/api/1.1/get/lists/subscribers/show
            :allowed_param:'owner_screen_name', 'slug', 'screen_name', 'owner_id', 'list_id', 'user_id
        """
        return bind_api(
            api=self,
            path='/lists/subscribers/show.json',
            payload_type='user',
            allowed_param=['owner_screen_name', 'slug', 'screen_name', 'owner_id', 'list_id', 'user_id']
        )

    @property
    def trends_available(self):
        """ :reference: https://dev.twitter.com/docs/api/1.1/get/trends/available """
        return bind_api(
            api=self,
            path='/trends/available.json',
            payload_type='json'
        )

    @property
    def trends_place(self):
        """ :reference: https://dev.twitter.com/docs/api/1.1/get/trends/place
            :allowed_param:'id', 'exclude
        """
        return bind_api(
            api=self,
            path='/trends/place.json',
            payload_type='json',
            allowed_param=['id', 'exclude']
        )

    @property
    def trends_closest(self):
        """ :reference: https://dev.twitter.com/docs/api/1.1/get/trends/closest
            :allowed_param:'lat', 'long
        """
        return bind_api(
            api=self,
            path='/trends/closest.json',
            payload_type='json',
            allowed_param=['lat', 'long']
        )

    @property
    def search(self):
        """ :reference: https://dev.twitter.com/docs/api/1.1/get/search
            :allowed_param:'q', 'lang', 'locale', 'since_id', 'geocode', 'max_id', 'since', 'until', 'result_type', 'count', 'include_entities', 'from', 'to', 'source']
        """
        return bind_api(
            api=self,
            path='/search/tweets.json',
            payload_type='search_results',
            allowed_param=['q', 'lang', 'locale', 'since_id', 'geocode', 'max_id', 'since', 'until', 'result_type',
                           'count', 'include_entities', 'from', 'to', 'source']
        )

    @property
    def trends_daily(self):
        """ :reference: https://dev.twitter.com/docs/api/1.1/get/trends/daily
            :allowed_param:'date', 'exclude
        """
        return bind_api(
            api=self,
            path='/trends/daily.json',
            payload_type='json',
            allowed_param=['date', 'exclude']
        )

    @property
    def trends_weekly(self):
        """ :reference: https://dev.twitter.com/docs/api/1.1/get/trends/weekly
            :allowed_param:'date', 'exclude
        """
        return bind_api(
            api=self,
            path='/trends/weekly.json',
            payload_type='json',
            allowed_param=['date', 'exclude']
        )

    @property
    def reverse_geocode(self):
        """ :reference: https://dev.twitter.com/docs/api/1.1/get/geo/reverse_geocode
            :allowed_param:'lat', 'long', 'accuracy', 'granularity', 'max_results
        """
        return bind_api(
            api=self,
            path='/geo/reverse_geocode.json',
            payload_type='place', payload_list=True,
            allowed_param=['lat', 'long', 'accuracy', 'granularity', 'max_results']
        )

    @property
    def geo_id(self):
        """ :reference: https://dev.twitter.com/docs/api/1.1/get/geo/id
            :allowed_param:'id
        """
        return bind_api(
            api=self,
            path='/geo/id/{id}.json',
            payload_type='place',
            allowed_param=['id']
        )

    @property
    def geo_search(self):
        """ :reference: https://dev.twitter.com/docs/api/1.1/get/geo/search
            :allowed_param:'lat', 'long', 'query', 'ip', 'granularity', 'accuracy', 'max_results', 'contained_within
        """
        return bind_api(
            api=self,
            path='/geo/search.json',
            payload_type='place', payload_list=True,
            allowed_param=['lat', 'long', 'query', 'ip', 'granularity', 'accuracy', 'max_results', 'contained_within']
        )

    @property
    def geo_similar_places(self):
        """ :reference: https://dev.twitter.com/docs/api/1.1/get/geo/similar_places
            :allowed_param:'lat', 'long', 'name', 'contained_within
        """
        return bind_api(
            api=self,
            path='/geo/similar_places.json',
            payload_type='place', payload_list=True,
            allowed_param=['lat', 'long', 'name', 'contained_within']
        )

    @property
    def supported_languages(self):
        """ :reference: https://dev.twitter.com/docs/api/1.1/get/help/languages """
        return bind_api(
            api=self,
            path='/help/languages.json',
            payload_type='json',
            require_auth=True
        )

    @property
    def configuration(self):
        """ :reference: https://dev.twitter.com/docs/api/1.1/get/help/configuration """
        return bind_api(
            api=self,
            path='/help/configuration.json',
            payload_type='json',
            require_auth=True
        )

    """ Internal use only """

    @staticmethod
    def _pack_image(filename, max_size, form_field="image", f=None):
        """Pack image from file into multipart-formdata post body"""
        # image must be less than 700kb in size
        if f is None:
            try:
                if os.path.getsize(filename) > (max_size * 1024):
                    raise TweepError('File is too big, must be less than 700kb.')
            except os.error:
                raise TweepError('Unable to access file')

            # build the mulitpart-formdata body
            fp = open(filename, 'rb')
        else:
            f.seek(0, 2)  # Seek to end of file
            if f.tell() > (max_size * 1024):
                raise TweepError('File is too big, must be less than 700kb.')
            f.seek(0)  # Reset to beginning of file
            fp = f

        # image must be gif, jpeg, or png
        file_type = mimetypes.guess_type(filename)
        if file_type is None:
            raise TweepError('Could not determine file type')
        file_type = file_type[0]
        if file_type not in ['image/gif', 'image/jpeg', 'image/png']:
            raise TweepError('Invalid file type for image: %s' % file_type)

        if isinstance(filename, unicode):
          filename = filename.encode("utf-8")
        filename = urllib.quote(filename)


        BOUNDARY = 'Tw3ePy'
        body = []
        body.append('--' + BOUNDARY)
        body.append('Content-Disposition: form-data; name="%s"; filename="%s"' % (form_field, filename))
        body.append('Content-Type: %s' % file_type)
        body.append('')
        body.append(fp.read())
        body.append('--' + BOUNDARY + '--')
        body.append('')
        fp.close()
        body = '\r\n'.join(body)

        # build headers
        headers = {
            'Content-Type': 'multipart/form-data; boundary=Tw3ePy',
            'Content-Length': str(len(body))
        }

        return headers, body
