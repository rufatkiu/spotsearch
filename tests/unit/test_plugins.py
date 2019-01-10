# -*- coding: utf-8 -*-

from unittest import TestCase
from searx import plugins
from mock import Mock


def get_search_mock(query, **kwargs):
    return Mock(query=query, answers=set(), **kwargs)


class PluginStoreTest(TestCase):

    def test_PluginStore_init(self):
        store = plugins.PluginStore()
        self.assertTrue(isinstance(store.plugins, list) and len(store.plugins) == 0)

    def test_PluginStore_register(self):
        store = plugins.PluginStore()
        testplugin = plugins.Plugin()
        store.register(testplugin)

        self.assertTrue(len(store.plugins) == 1)

    def test_PluginStore_call(self):
        store = plugins.PluginStore()
        testplugin = plugins.Plugin()
        store.register(testplugin)
        setattr(testplugin, 'asdf', Mock())
        request = Mock()
        store.call([], 'asdf', request, Mock())

        self.assertFalse(testplugin.asdf.called)

        store.call([testplugin], 'asdf', request, Mock())
        self.assertTrue(testplugin.asdf.called)


class SelfIPTest(TestCase):

    def test_PluginStore_init(self):
        store = plugins.PluginStore()
        store.register(plugins.self_info)

        self.assertTrue(len(store.plugins) == 1)

        # IP test
        request = Mock(remote_addr='127.0.0.1')
        request.headers.getlist.return_value = []
        search = get_search_mock(query='ip', pageno=1)
        store.call(store.plugins, 'post_search', request, search)
        self.assertTrue('127.0.0.1' in search.answers)

        search = get_search_mock(query='ip', pageno=2)
        store.call(store.plugins, 'post_search', request, search)
        self.assertFalse('127.0.0.1' in search.answers)

        # User agent test
        request = Mock(user_agent='Mock')
        request.headers.getlist.return_value = []

        search = get_search_mock(query='user-agent', pageno=1)
        store.call(store.plugins, 'post_search', request, search)
        self.assertTrue('Mock' in search.answers)

        search = get_search_mock(query='user-agent', pageno=2)
        store.call(store.plugins, 'post_search', request, search)
        self.assertFalse('Mock' in search.answers)

        search = get_search_mock(query='user-agent', pageno=1)
        store.call(store.plugins, 'post_search', request, search)
        self.assertTrue('Mock' in search.answers)

        search = get_search_mock(query='user-agent', pageno=2)
        store.call(store.plugins, 'post_search', request, search)
        self.assertFalse('Mock' in search.answers)

        search = get_search_mock(query='What is my User-Agent?', pageno=1)
        store.call(store.plugins, 'post_search', request, search)
        self.assertTrue('Mock' in search.answers)

        search = get_search_mock(query='What is my User-Agent?', pageno=2)
        store.call(store.plugins, 'post_search', request, search)
        self.assertFalse('Mock' in search.answers)
