# coding=utf-8

# Bindings for the Open Text Summarizer library
#
# Copyright (C) 2011 Justus Winter <4winter@informatik.uni-hamburg.de>
#
# Permission to use, copy, modify, and distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

import ctypes
import ctypes.util

try:
    libc = ctypes.cdll.LoadLibrary(ctypes.util.find_library('c'))
except OSError as e:
    raise ImportError('Could not load libc: %s' % e)

try:
    libots = ctypes.cdll.LoadLibrary(ctypes.util.find_library('ots-1'))
except OSError as e:
    raise ImportError('Could not load libots: %s' % e)

free = libc.free
free.argtypes = [ctypes.c_void_p]
free.restype = None

story = \
'This is a story about a brown fox. The fox jumps quickly over a ' \
'''lazy dog, while it is lying in the sun enjoying his day off.

The fox was really quick and the dog even lazier. Oh well. What's ''' \
'the point of all this?'

class OtsArticle(object):
    r'''
    >>> ots_article = OtsArticle()
    >>> ots_article.load_dictionary()
    >>> ots_article.parse(story)
    >>> ots_article.grade()
    >>> ots_article.title
    ['fox', 'dog', 'quickly', 'point', 'lazier']
    >>> ots_article.highlight_words(10)
    >>> ots_article.get_text()
    'The fox jumps quickly over a lazy dog, while it is lying in the sun enjoying his day off.'
    '''
    class OtsArticle_s(ctypes.Structure):
        _fields_ = [
            ('lines', ctypes.c_void_p),
            ('line_count', ctypes.c_int),
            ('title', ctypes.c_char_p),
            # ...
        ]
    OtsArticle_p = ctypes.POINTER(OtsArticle_s)

    @property
    def title(self):
        return self.pointer.contents.title.split(',')

    _ots_new_article = libots.ots_new_article
    _ots_new_article.argtypes = []
    _ots_new_article.restype = OtsArticle_p

    def __init__(self):
        self.pointer = self._ots_new_article()

    _ots_free_article = libots.ots_free_article
    _ots_free_article.argtypes = [OtsArticle_p]
    _ots_free_article.restype = None

    def __del__(self):
        self._ots_free_article(self.pointer)

    _ots_parse_stream = libots.ots_parse_stream
    _ots_parse_stream.argtypes = [ctypes.c_char_p, ctypes.c_size_t, OtsArticle_p]
    _ots_parse_stream.restype = None

    def parse(self, text):
        text_u = text.encode('utf-8')
        self._ots_parse_stream(text_u, len(text_u), self.pointer)

    class AllocatedString(ctypes.c_char_p):
        def __del__(self):
            free(self)

    _ots_get_doc_text = libots.ots_get_doc_text
    _ots_get_doc_text.argtypes = [OtsArticle_p, ctypes.POINTER(ctypes.c_size_t)]
    _ots_get_doc_text.restype = AllocatedString

    def get_text(self):
        result_p = self._ots_get_doc_text(self.pointer, None)
        return result_p.value.decode('utf-8').strip()

    _ots_load_xml_dictionary = libots.ots_load_xml_dictionary
    _ots_load_xml_dictionary.argtypes = [OtsArticle_p, ctypes.c_char_p]
    _ots_load_xml_dictionary.restype = bool

    def load_dictionary(self, language = 'en'):
        if not self._ots_load_xml_dictionary(self.pointer, language):
            raise RuntimeError('Loading dictionary %s failed' % language)

    _ots_grade_doc = libots.ots_grade_doc
    _ots_grade_doc.argtypes = [OtsArticle_p]
    _ots_grade_doc.restype = None

    def grade(self):
        self._ots_grade_doc(self.pointer)

    _ots_highlight_doc = libots.ots_highlight_doc
    _ots_highlight_doc.argtypes = [OtsArticle_p, ctypes.c_int]
    _ots_highlight_doc.restype = None

    def highlight(self, percentage):
        self._ots_highlight_doc(self.pointer, percentage)

    _ots_highlight_doc_lines = libots.ots_highlight_doc_lines
    _ots_highlight_doc_lines.argtypes = [OtsArticle_p, ctypes.c_int]
    _ots_highlight_doc_lines.restype = None

    def highlight_lines(self, lines):
        self._ots_highlight_doc_lines(self.pointer, lines)

    _ots_highlight_doc_words = libots.ots_highlight_doc_words
    _ots_highlight_doc_words.argtypes = [OtsArticle_p, ctypes.c_int]
    _ots_highlight_doc_words.restype = None

    def highlight_words(self, words):
        self._ots_highlight_doc_words(self.pointer, words)
