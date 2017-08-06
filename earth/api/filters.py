from django.db import models


class Filter(object):
    GLOBAL = 'global'
    SOURCE_SPECIFIC = 'specific'
    TYPES_CHOICES = (
        (GLOBAL, 'Global'),
        (SOURCE_SPECIFIC, 'Source specific')
    )
    TYPES = tuple(t[0] for t in TYPES_CHOICES)

    def __init__(self, type=None, source=None, *args, **kwargs):
        assert type in self.TYPES
        self.type = type
        if type == self.SOURCE_SPECIFIC:
            assert source is not None
        self.source = source
        self.global_exclusion_query = None

    def set_exclusion_query(self, query):
        operating_query = query
        if self.type == self.SOURCE_SPECIFIC:
            self.global_exclusion_query = query.exclude(source=self.source)
            operating_query = query.filter(source=self.source)

        return operating_query

    def filter(self, *args, **kwargs):
        raise NotImplementedError()

    def __call__(self, query):
        operating_query = self.set_exclusion_query(query)
        filtered_set = self.filter(operating_query)
        if self.global_exclusion_query is not None:
            filtered_set |= self.global_exclusion_query

        return filtered_set


class TitleKeyWordFilter(Filter):

    def __init__(self, *args, key_words=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.key_words = key_words

    def filter(self, query):
        query_kwargs = [models.Q(title__icontains=kw.strip())
                        for kw in self.key_words.split(',')]
        query_parameters = query_kwargs.pop()
        for item in query_kwargs:
            query_parameters |= item

        return query.filter(query_parameters)



class ResolutionFilter(Filter):

    def __init__(self, *args, resolution_type=None, resolution_threshold_operand=None,
                 resolution_value=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.resolution_type = resolution_type
        self.resolution_threshold_operand = resolution_threshold_operand
        self.resolution_value = resolution_value

    def filter(self, query):
        resolution_query = 'resolution_{type}__{operator}'.format(
            type=self.resolution_type,
            operator=self.resolution_threshold_operand)
        return query\
            .filter(**{resolution_query: self.resolution_value})


class ScoreFilter(Filter):

    def __init__(self, *args, score_type, score_threshold_operand,
                 score_value, **kwargs):
        super().__init__(*args, **kwargs)
        self.score_type = score_type
        self.score_threshold_operand = score_threshold_operand
        self.score_value = score_value

    def filter(self, query):
        score_query = '{type}__{operator}'.format(
            type=self.score_type,
            operator=self.score_threshold_operand)
        return query\
            .filter(**{score_query: self.score_value})

