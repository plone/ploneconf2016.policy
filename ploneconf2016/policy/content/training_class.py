from plone import api
from plone.indexer.decorator import indexer
from plone.supermodel import model
from plone.dexterity.browser.view import DefaultView
from .vocabularies import TRAINING_CLASS_DURATION_TYPES, LEVEL_TYPES, \
AUDIENCE_TYPES

class ITrainingClass(model.Schema):
    model.load('models/training_class.xml')


class TrainingClassView(DefaultView):

    def duration_vocab(self):
        return TRAINING_CLASS_DURATION_TYPES

    def level_vocab(self):
        return LEVEL_TYPES

    def audience_vocab(self):
        return AUDIENCE_TYPES

    def instructors(self):
        """ parse instructor set into something template can iterate over
        """        
        instructor_set = self.context.instructor
        instructors = [api.content.get(UID=x) for x in instructor_set]
        instructor_data = []
        for x in instructors:
            if x:
                instructor_data.append({'url':x.absolute_url(), 'name': x.title})
        return instructor_data

    def vocab_title(self, values, vocab):
        """ return title when given the vocabulary and the value key
        """
        if not isinstance(values, (list, set)):
            result = vocab.getTerm(values).title
            if vocab == AUDIENCE_TYPES:
                return [result] # hacky fix
            return result
        return [vocab.getTerm(x).title for x in values ]
