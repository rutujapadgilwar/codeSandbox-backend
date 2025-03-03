from graphene import ObjectType, Schema

import polls.schema

class Query(
    polls.schema.Query,
    ObjectType,
):
    pass


class Mutation(
    polls.schema.Mutation,
    ObjectType,
):
    pass


schema = Schema(query=Query, mutation=Mutation)
