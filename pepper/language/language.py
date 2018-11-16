from pepper.language.ner import NER

from random import getrandbits
from nltk import pos_tag, CFG, RecursiveDescentParser

import logging
import enum
import json
import re
import os


class UtteranceType(enum.Enum):
    STATEMENT = 0
    QUESTION = 1


class Chat(object):
    def __init__(self, speaker):
        """
        Create Chat

        Parameters
        ----------
        speaker: str
            Name of speaker (a.k.a. the person Pepper has a chat with)
        """
        # TODO: Add contextual information (e.g. datetime, location, ...)

        self._id = getrandbits(128)
        self._speaker = speaker
        self._utterances = []

    @property
    def id(self):
        """
        Returns
        -------
        id: int
            Unique (random) identifier of this chat
        """
        return self._id

    @property
    def speaker(self):
        """
        Returns
        -------
        speaker: str
            Name of speaker (a.k.a. the person Pepper has a chat with)
        """
        return self._speaker

    @property
    def utterances(self):
        """
        Returns
        -------
        utterances: list of Utterance
            List of utterances that occurred in this chat
        """
        return self._utterances

    @property
    def last_utterance(self):
        """
        Returns
        -------
        last_utterance: Utterance
            Most recent Utterance
        """
        return self._utterances[-1]

    def add_utterance(self, text):
        """
        Add Utterance to Conversation

        Parameters
        ----------
        text: str
            Utterance Text to add to conversation

        Returns
        -------
        utterance: Utterance
        """
        utterance = Utterance(text, self._speaker, self._id, len(self._utterances))
        self._utterances.append(utterance)
        return utterance


class Utterance(object):
    def __init__(self, transcript, speaker, chat_id, chat_turn):
        """
        Construct Utterance Object

        Parameters
        ----------
        transcript: str
            Uttered text (Natural Language)
        speaker: str
            Speaker name
        chat_id: int
            Unique chat identifier
        chat_turn: int
            Chat turn
        """

        # TODO: Add Viewed Objects!

        self._transcript = transcript
        self._tokens = self._clean(self._tokenize(transcript))
        self._speaker = speaker.lower()
        self._chat_id = chat_id
        self._chat_turn = chat_turn

    @property
    def transcript(self):
        """
        Returns
        -------
        transcript: str
        """
        return self._transcript

    @property
    def tokens(self):
        """
        Returns
        -------
        tokens: list of str
            Tokenized transcript
        """
        return self._tokens

    @property
    def speaker(self):
        """
        Returns
        -------
        speaker: str
            Speaker name
        """
        return self._speaker

    @property
    def chat_id(self):
        """
        Returns
        -------
        chat_id: int
            Unique chat identifier
        """
        return self._chat_id

    @property
    def chat_turn(self):
        """
        Returns
        -------
        chat_turn: int
            Chat turn
        """
        return self._chat_turn

    def _tokenize(self, transcript):
        """
        Parameters
        ----------
        transcript: str
            Uttered text (Natural Language)

        Returns
        -------
        tokens: list of str
            Tokenized transcript: list of cleaned tokens
                - remove contractions
        """

        tokens_raw = transcript.split()
        tokens = []
        for word in tokens_raw:
            clean_word = re.sub('[?!]', '', word)
            tokens.append(clean_word.lower())
        return tokens

    def _clean(self, tokens):
        """
        Parameters
        ----------
        tokens: list of str
            Tokenized transcript

        Returns
        -------
        cleaned_tokens: list of str
            Tokenized & Cleaned transcript
        """

        # TODO: Remove Contractions

        return tokens

class Parser(object):

    CFG_GRAMMAR_FILE = os.path.join(os.path.dirname(__file__), 'cfg.txt')

    def __init__(self):
        with open(Parser.CFG_GRAMMAR_FILE) as cfg_file:
            self._cfg = cfg_file.read()

    def parse(self, chat):
        last_utterance = chat.utterances[-1]
        tokenized_sentence = last_utterance.tokens
        pos = pos_tag(tokenized_sentence)
        #print(pos)
        for el in pos:
            if el[1].endswith('$'):
                new_rule = el[1][:-1] + 'POS -> \'' + el[0] + '\'\n'
            else:
                new_rule = el[1] + ' -> \'' + el[0] + '\'\n'
            if new_rule not in self._cfg:
                self._cfg += new_rule

        cfg_parser = CFG.fromstring(self._cfg)
        RD = RecursiveDescentParser(cfg_parser)
        parsed = RD.parse(tokenized_sentence)
        return parsed


class Analyzer(object):

    # Load Grammar Json
    GRAMMAR_JSON = os.path.join(os.path.dirname(__file__), 'grammar.json')
    with open(GRAMMAR_JSON) as json_file:
        GRAMMAR = json.load(json_file)['grammar']

    # Load Stanford Named Entity Recognition Server
    STANFORD_NER = NER('english.muc.7class.distsim.crf.ser')

    def __init__(self, chat):
        """
        Abstract Analyzer Object: call Analyzer.analyze(utterance) factory function

        Parameters
        ----------
        chat: Chat
            Chat to be analyzed
        """

        self._chat = chat
        self._log = logging.getLogger(self.__class__.__name__)

    @staticmethod
    def analyze(parsed_tree):
        """
        Analyzer factory function

        Find appropriate Analyzer for this utterance

        Parameters
        ----------
        chat: Chat
            Chat to be analyzed

        Returns
        -------
        analyzer: Analyzer
            Appropriate Analyzer Subclass
        """

        print(parsed_tree)


        '''
        if chat.last_utterance.tokens:
            first_token = chat.last_utterance.tokens[0]

            question_words = Analyzer.GRAMMAR['question words'].keys()
            to_be = Analyzer.GRAMMAR['to be'].keys()
            modal_verbs = Analyzer.GRAMMAR['modal_verbs']

            question_cues = question_words + to_be + modal_verbs

            # Classify Utterance as Question / Statement
            if first_token in question_cues:
                return QuestionAnalyzer.analyze(chat)
            else:
                return StatementAnalyzer.analyze(chat)
        else:
            raise ValueError("Utterance should have at least one element")
        '''

    @property
    def log(self):
        """
        Returns
        -------
        log: logging.Logger
        """
        return self._log

    @property
    def chat(self):
        """
        Returns
        -------
        chat: Chat
            Chat to be analyzed
        """
        return self._chat

    @property
    def utterance_type(self):
        """
        Returns
        -------
        utterance_type: UtteranceType
            Utterance Type
        """
        return NotImplementedError()

    @property
    def rdf(self):
        """
        Returns
        -------
        rdf: dict or None
        """
        raise NotImplementedError()

    @property
    def template(self):
        """
        Returns
        -------
        template: dict or None
        """

        # TODO: Implement here!

        return None

'''
class StatementAnalyzer(Analyzer):
    """Abstract StatementAnalyzer Object: call StatementAnalyzer.analyze(utterance) factory function"""

    @staticmethod
    def analyze(chat):
        """
        StatementAnalyzer factory function

        Find appropriate StatementAnalyzer for this utterance

        Parameters
        ----------
        chat: Chat
            Chat to be analyzed

        Returns
        -------
        analyzer: StatementAnalyzer
            Appropriate StatementAnalyzer Subclass
        """

        return GeneralStatementAnalyzer(chat)

    @property
    def utterance_type(self):
        """
        Returns
        -------
        utterance_type: UtteranceType
            Utterance Type (Statement)
        """
        return UtteranceType.STATEMENT

    @property
    def rdf(self):
        """
        Returns
        -------
        rdf: dict or None
        """
        raise NotImplementedError()


class GeneralStatementAnalyzer(StatementAnalyzer):
    def __init__(self, chat):
        """
        General Statement Analyzer

        Parameters
        ----------
        chat: Chat
            Chat to be analyzed
        """

        super(GeneralStatementAnalyzer, self).__init__(chat)

        # TODO: Implement Chat -> RDF

        self._rdf = {}

    @property
    def rdf(self):
        """
        Returns
        -------
        rdf: dict or None
        """
        return self._rdf


class ObjectStatementAnalyzer(StatementAnalyzer):
    def __init__(self, chat):
        """
        Object Statement Analyzer

        Parameters
        ----------
        chat: Chat
        """

        super(ObjectStatementAnalyzer, self).__init__(chat)

        # TODO: Implement Chat -> RDF

        self._rdf = {}

    @property
    def rdf(self):
        """
        Returns
        -------
        rdf: dict or None
        """
        return self._rdf


class QuestionAnalyzer(Analyzer):
    """Abstract QuestionAnalyzer Object: call QuestionAnalyzer.analyze(utterance) factory function"""

    @staticmethod
    def analyze(chat):
        """
        QuestionAnalyzer factory function

        Find appropriate QuestionAnalyzer for this utterance

        Parameters
        ----------
        chat: Chat
            Chat to be analyzed

        Returns
        -------
        analyzer: QuestionAnalyzer
            Appropriate QuestionAnalyzer Subclass
        """
        if chat.last_utterance.tokens:
            first_word = chat.last_utterance.tokens[0]

            if first_word in Analyzer.GRAMMAR['question words']:
                return WhQuestionAnalyzer(chat)
            else:
                return VerbQuestionAnalyzer(chat)

    @property
    def utterance_type(self):
        """
        Returns
        -------
        utterance_type: UtteranceType
            Utterance Type (Question)
        """
        return UtteranceType.QUESTION

    @property
    def rdf(self):
        """
        Returns
        -------
        rdf: dict or None
        """
        raise NotImplementedError()


class WhQuestionAnalyzer(QuestionAnalyzer):
    def __init__(self, chat):
        """
        Wh-Question Analyzer

        Parameters
        ----------
        chat: Chat
        """

        super(WhQuestionAnalyzer, self).__init__(chat)

        # TODO: Implement Chat -> RDF

        self._rdf = {}

    @property
    def rdf(self):
        """
        Returns
        -------
        rdf: dict or None
        """
        return self._rdf


class VerbQuestionAnalyzer(QuestionAnalyzer):
    def __init__(self, chat):
        """
        Verb Question Analyzer

        Parameters
        ----------
        chat: Chat
        """

        super(VerbQuestionAnalyzer, self).__init__(chat)

        # TODO: Implement Chat -> RDF

        self._rdf = {}

    @property
    def rdf(self):
        """
        Returns
        -------
        rdf: dict or None
        """
        return self._rdf
'''

if __name__ == '__main__':
    chat = Chat("Bram")
    chat.add_utterance("I like bananas")
    cfg_parser = Parser()
    parsed_tree = cfg_parser.parse(chat)
    analyzer = Analyzer.analyze(parsed_tree)

    print(analyzer.__class__.__name__)
