from plone.restapi.interfaces import IFieldSerializer
from plone.restapi.serializer.converters import json_compatible
from plone.restapi.serializer.dxfields import DefaultFieldSerializer
from plone.dexterity.interfaces import IDexterityContent
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.interface import Interface
from zope.interface import implementer
from plone.app.uuid.utils import uuidToObject
from zope.schema.interfaces import ISet
from zope.schema.interfaces import IField

from .content.training_class import ITrainingClass


def getSiteRootRelativePath(context, request):
    """ Get site root relative path to an item
    @param context: Content item which path is resolved
    @param request: HTTP request object
    @return: Path to the context object, relative to site root, prefixed with a slash.
    """

    portal_state = getMultiAdapter((context, request), name=u"plone_portal_state")
    site = portal_state.portal()

    # Both of these are tuples
    site_path = site.getPhysicalPath()
    context_path = context.getPhysicalPath()

    relative_path = context_path[len(site_path) :]

    return "/" + "/".join(relative_path)


@adapter(ISet, ITrainingClass, Interface)
@implementer(IFieldSerializer)
class TrainingClassSetFieldSerializer(DefaultFieldSerializer):
    def __init__(self, field, context, request):
        self.context = context
        self.request = request
        self.field = field

    def __call__(self):
        if IField.providedBy(self.field):  # Binding is necessary for named vocabularies
            self.field = self.field.bind(self.context)

        value = self.get_value()
        value_type = self.field.value_type
        collection_to_serialize = []

        for item in value:
            term = value_type.vocabulary.getTerm(item)
            item_to_serialize = {
                u"token": term.token,
                u"title": term.title,
            }
            obj = uuidToObject(item)
            if IDexterityContent.providedBy(obj):
                # If obj is a Dexterity Content type, we can provide a site_root_relative_url
                item_to_serialize["site_root_relative_url"] = getSiteRootRelativePath(
                    obj, self.request
                )
            collection_to_serialize.append(item_to_serialize)

        return json_compatible(collection_to_serialize)
