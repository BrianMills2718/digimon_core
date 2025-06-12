Meet TypeDB and TypeQL
TypeDB is a polymorphic database with a conceptual data model, a strong subtyping system, a symbolic reasoning engine, and a beautiful and elegant type-theoretic language: TypeQL.

Visit learning center
Read philosophy
Conceptual Modeling
Entity-Relation-Attribute
TypeQL implements the Enhanced Entity-Relation-Attribute model for its schemas and data. Entities, relations, and attributes are all first-class citizens and subtypable, allowing for expressive modeling without normalization or reification.

1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
26
27
28
29
30
31
32
33

define

  id sub attribute, value string;
  email sub id;
  path sub id;
  name sub id;

  user sub entity,
    owns email @unique,
    plays permission:subject,
    plays request:requester;
  file sub entity,
    owns path,
    plays permission:object;
  action sub entity,
    owns name,
    plays permission:action;

  permission sub relation,
    relates subject,
    relates object,
    relates action,
    plays request:target;
  request sub relation,
    relates target,
    relates requester;
Declarative Schema
The schema provides a structural blueprint for data organization, ensuring referential integrity in production. Extend your data model seamlessly in TypeDB, maintaining integrity during model updates and avoiding any query rewrites or code refactors.

1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
26
27
28
29
30
31
32
33

define

  full-name sub attribute, value string;
  id sub attribute, value string;
  email sub id;
  employee-id sub id;

  user sub entity,
    owns full-name,
    owns email @unique;
  employee sub user,
    owns employee-id @key;
Abstract Types
Define abstract entity, relation, and attribute types in your schema to extend concrete types from. Build templates with ownership of abstract attributes and playing of abstract roles for subtypes to extend and override.

1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
26
27
28
29
30
31
32
33

define

  id sub attribute, abstract, value string;
  email sub id;
  path sub id;

  user sub entity, abstract,
    owns id;
  employee sub user,
    owns email as id;
  resource sub entity, abstract,
    owns id,
    plays collection-membership:member;
  file sub resource,
    owns path as id;

  membership sub relation, abstract,
    relates parent,
    relates member;
  team-membership sub membership,
    relates team as parent;
  collection-membership sub membership,
    relates collection as parent;
Type Inheritance
Type inheritance in TypeDB allows you to create new types based on existing ones, providing hierarchy and abstraction in your data model. By inheriting attributes and relationships from parent types, schema design is simplified, promoting reusability and consistency.

1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
26
27
28
29
30
31
32
33

define
  user sub entity,
    owns full-name,
    owns email;
  intern sub user;
  employee sub user,
    owns employee-id,
    owns title;
  part-time-employee sub employee,
    owns weekly-hours;
Strong Type System
Type Inference
TypeDB’s type inference resolves queries against the schema to generate polymorphic results. Queries on supertypes automatically return results for subtypes, and the types of variables can even be omitted to match only the shape of the data.

1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
26
27
28
29
30
31
32
33

define
  user sub entity, abstract,
    owns id,
    plays resource-ownership:owner;
  employee sub user, owns employee-id as id;
  resource sub entity, abstract,
    owns id,
    plays resource-ownership:resource;
  file sub resource, owns path as id;
  database sub resource, owns name as id;
  commit sub resource, owns hash as id;
  resource-ownership sub relation,
    relates resource,
    relates owner;

match
  $user has id $user-id;
  $rsrc has id $rsrc-id;
  ($user, $rsrc) isa $relation-type;
fetch
  $user-id;
  $rsrc-id;
  $relation-type;

Semantic Validation
TypeDB validates all queries and rules against the type system defined in the schema to ensure semantic correctness. Nonsensical writes are automatically blocked, and nonsensical reads throw an exception instead of returning an empty result set.

1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
26
27
28
29
30
31
32
33

define
  weekly-hours sub attribute value long;
  full-time-employee sub employee;
  part-time-employee sub employee, owns weekly-hours;

  insert
    $francois isa full-time-employee,
      has full-name "François Durand",
      has email "francois@typedb.com",
      has employee-id 184,
      has weekly-hours 35;

# [THW03] Invalid Write: Attribute of type 'weekly-hours' is
# not defined to be owned by type 'full-time-employee'.
Symbolic Reasoning
Rule-Based Reasoning
TypeDB’s symbolic reasoning enables the automated deduction of new facts and relationships based on existing data and rules you define. Rule chaining and branching allow complex behavior to arise from simple rules, creating rich, high-level insights.

1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
26
27
28
29
30
31
32
33

define

  rule transitive-team-membership:
    when {
      (team: $team-1, member: $team-2) isa team-membership;
      (team: $team-2, member: $member) isa team-membership;
    } then {
      (team: $team-1, member: $member) isa team-membership;
    };

  rule inherited-team-permission:
    when {
      (team: $team, member: $member) isa team-membership;
      (subject: $team, object: $obj, action: $act) isa permission;
    } then {
      (subject: $member, object: $obj, action: $act) isa inherited-permission;
    };

Explanations
TypeDB's reasoning engine functions on deductive reasoning, so inferred data can always be traced back to its source. Perform root-cause analysis using TypeDB’s Explanations feature, guaranteeing accountability of generated data.

1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
26
27
28
29
30
31
32
33

query = "match $perm isa inherited-permission; get;"

with open_session.transaction(TransactionType.READ) as tx:
    results = tx.query().get(query)
    for result in results:
        inherited_permission = result.explainables().relation("perm")
        explanations = tx.query().explain(inherited_permission)
        for explanation in explanations:
            condition = explanation.condition()
            rule = explanation.rule()
            conclusion = explanation.conclusion()
Polymorphic Queries
Variablized Types
Schema types and relation roles can be variablized in addition to data instances, making schema querying as easy as data querying. Queries can contain both schema and data constraints, allowing for patterns that represent highly complex conceptual structures.

1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
26
27
28
29
30
31
32
33

define
  user sub entity, has full-name,
    plays mentorship:mentor,
    plays mentorship:trainee;
  employee sub user;
  contractor sub user;
  mentorship sub relation,
    relates mentor,
    relates trainee;

match
  $user isa $user-type, has full-name $name;
  $user-type sub user;
  ($role-1: $user, $role-2: $other-user) isa mentorship;
  mentorship relates $role-1, relates $role-2;
fetch
  $name;
  $user-type;
  $role-1;
  $role-2;

Inheritance Polymorphism
TypeQL implements inheritance polymorphism, allowing subtypes to inherit the behaviors of the supertypes they extend, whether concrete or abstract. Write TypeQL queries that return results with a common supertype, without enumerating the subtypes.

1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
26
27
28
29
30
31
32
33

define
  user sub entity,
    owns full-name,
    owns email @unique;
  employee sub user,
    owns employee-id @key;

insert
  $john isa employee,
    has full-name "John Doe",
    has email "john@typedb.com",
    has employee-id 183;
Interface Polymorphism
Ensure conceptual consistency between defined types and their behaviors in perfect parallel to your object model by harnessing TypeQL’s interface polymorphism. Types can own the same attributes and play the same roles, even if they share no common supertypes.

1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
26
27
28
29
30
31
32
33

define
  name sub attribute, value string;
  user sub entity, owns name;
  team sub entity, owns name;
  table sub entity, owns name;

match
  $x has name $n;
fetch
  $n;
Parametric Polymorphism
Write queries that create or delete data instances without specifying their types by utilizing parametric polymorphism. Queries are resolved against the schema when run, allowing them to write data of multiple types matching declared properties.

1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
26
27
28
29
30
31
32
33

match
  $data isa $T;
  $data has data-expiration-date < 2023-09-27;
delete
  $data isa $T;
Modern Language
Near Natural
Due to its OOP properties and simple syntax, queries written in TypeQL read close to natural language. Domain experts and non-technical users alike can quickly grasp the intent of a query, reducing the learning curve and making query maintenance a breeze.

1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
26
27
28
29
30
31
32
33

match
  $kevin isa user, has email "kevin@typedb.com";
insert
  $chloe isa part-time-employee,
    has full-name "Chloé Dupond",
    has email "chloe@typedb.com",
    has employee-id 185,
    has weekly-hours 35;
  $hire (employee: $chloe, ceo: $kevin) isa hiring,
    has date 2023-09-27;
Fully Declarative
TypeQL is fully declarative, allowing you to define query patterns without considering execution strategy. TypeDB’s query planner always deconstructs queries into the most optimized plans, so you never have to think about the logical implementation.

1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
26
27
28
29
30
31
32
33

define
  user sub entity,
    owns full-name,
    owns email;
  intern sub user;
  employee sub user,
    owns employee-id;
  full-time-employee sub employee;
  part-time-employee sub employee,
    owns weekly-hours;
  contractor sub user,
    owns contract-number;

match
  $user isa $user-type;
  $user-type sub user;
fetch
  $user: attribute;
  $user-type;
Composable Patterns
Patterns in TypeQL are fully composable. Every complex pattern can be broken down into a conjunction of atomic constraints, which can be concatenated in any order. Any pattern composed of valid constraints is guaranteed to be valid itself, no matter how complex.

1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
26
27
28
29
30
31
32
33

match
  $user isa user;
fetch
  $user: full-name; 

match
  $user isa user;
  $user has email "john@typedb.com";
fetch
  $user: full-name; 

match
  $user isa user;
  $user has email "john@typedb.com";
  (team: $team, member: $user) isa team-membership;
fetch
  $user: full-name;

match
  $user isa user;
  $user has email "john@typedb.com";
  (team: $team, member: $user) isa team-membership;
  $team has name "Engineering";
fetch
  $user: full-name;

Nested Subqueries
Search for complex data structures with a single query and network trip using nested subqueries. Retrieve results for nested queries as a list or perform aggregations over them, including results for optional attribute matches.

1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
26
27
28
29
30
31
32
33

match
  $user isa user;
fetch
  $user: email, full-name, employee-id;
  teams: {
    match
      (team: $team, member: $user) isa team-membership;
    fetch
      $team: name;
  };
  permission-count: {
    match
      $perm (subject: $user) isa permission;
    get;
    count;
  };

Structured Results
Query results can be serialized for easy consumption in your application with TypeQL’s native JSON outputs. Switch from an asynchronous answer stream to a single structured collection, and define the result format using projections in the query structure.

1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
26
27
28
29
30
31
32
33

match
  $user isa full-time-employee;
fetch
  $user as employee: attribute;
limit 1;

# JSON output:
[{
    "employee": {
        "type": { "root": "entity", "label": "full-time-employee" },
	"attribute": [
            { "value": "Chloé Dupond", "value_type": "string", "type": { "root": "attribute", "label": "full-name" } },
            { "value": "chloe@typedb.com", "value_type": "string", "type": { "root": "attribute", "label": "email" } },
            { "value": 185, "value_type": "long", "type": { "root": "attribute", "label": "employee-id" } },
            { "value": 35, "value_type": "long", "type": { "root": "attribute", "label": "weekly-hours" } }
        ]
    }
}]

Aggregates and Expressions
Perform basic mathematical operations directly in your queries or rules with aggregations and arithmetic expressions, enabling dynamic and efficient data computation.

1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
26
27
28
29
30
31
32
33

match
  $user isa user;
  $perm (subject: $user) isa permission;
group $user;
get;
count;

match
  $dir isa directory,
    has path $path,
    has size $kb;
  ?gb = $kb / 1024 ^ 2;
fetch
  $path;
  ?gb;

Query Builder
Use the TypeQL query builder to auto-generate queries using a code-first approach in Java or Rust, with other languages coming soon. This permits the generation of TypeDB queries through a robust and streamlined process.

1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
26
27
28
29
30
31
32
33

TypeQLMatch.Filtered builtQuery = TypeQL.match(
    cVar("user").isa("user").has("full-name", "Kevin Morrison"),
    cVar("file").isa("file").has("path", cVar("path")),
    cVar("perm").rel(cVar("user")).rel(cVar("file")).isa("permission")
).get(cVar("path"));

// builtQuery =
// match
//   $user isa user, has full-name 'Kevin Morrison'; 
//   $file isa file, has path $path;
//   $perm ($user, $file) isa permission;
// get $path;
Query Templates
3.0 Roadmap
Build query templates that accept a tuple of attribute values as parameters and execute them repeatedly for lists of supplied values. The template is stored in the transaction cache, reducing network load and ensuring sanitization of input strings.

Expressive Relations
N-ary Relations
Construct rich data representations by directly implementing unary, binary, ternary, and n-ary relations in your conceptual model. TypeQL’s expressivity allows you to use the same constructor format for all relations, regardless of the number of roleplayers.

1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
26
27
28
29
30
31
32
33

match
  $omar isa contractor, has email "omar@typedb.com";
insert 
  $term (user: $omar) isa user-termination,
    has termination-date 2023-09-19,
    has termination-reason "end of contract";

match
  $naomi isa user, has email "naomi@typedb.com";
  $eng isa group, has name "Engineering";
insert
  $own (group: $eng, owner: $naomi) isa group-ownership;

match
  $john isa user, has email "john@typedb.com";
  $readme isa file, has path "/usr/johndoe/repos/typedb/readme.md";
  $edit isa action, has name "edit file";
insert
  $perm (subject: $john, object: $readme, action: $edit) isa permission;
Nested Relations
Relations are first-class citizens in TypeQL and so can own attributes and play roles in other relations just like entities. With no limit to the depth of nesting for relations, you can express the full richness of your data without reifying your data model.

1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
26
27
28
29
30
31
32
33

match
  $john isa user, has email "john@typedb.com";
  $readme isa file, has path "/usr/johndoe/repos/typedb/readme.md";
  $edit isa action, has name "edit file";
  $perm (subject: $john, object: $readme, action: $edit) isa permission;
  $kevin isa user, has email "kevin@typedb.com";
insert
  $rqst (target: $perm, requestee: $kevin) isa change-request,
    has requested-change "revoke";

Variadic Relations
With TypeQL’s expressive relation constructor, you can easily implement relations where the same roleplayer plays multiple roles, multiple roleplayers play the same role, or a combination of both. Read queries always return all matched roleplayers.

1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
26
27
28
29
30
31
32
33

match
  $submit isa action, has name "submit order";
  $approve isa action, has name "approve order";
insert
  (segregated-action: $submit, segregated-action: $approve) isa segregation-policy;

match
  $kevin isa user, has email "kevin@typedb.com";
insert
  (reviewer: $kevin, reviewee: $kevin) isa permission-review;
Cardinality Constraints
3.0 Roadmap
All attributes and relations have many-to-many cardinality by default. Apply constraints in the schema to apply stricter cardinalities wherever needed, with the expressivity to select a single value or a specific range.

1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
26
27
28
29
30
31
32
33

define

  name sub attribute, value string;
  object-type sub attribute, value string;

  action sub entity,
    owns name @card(1),
    owns object-type @card(1,*)
    plays segregation-policy:segregated-action @card(0,*);

  segregation-policy sub relation,
    relates segregated-action @card(2);
Intuitive Attributes
Multi-Valued Attributes
TypeQL is a conceptual data modeling language, and all attributes have many-to-many cardinality by default. Giving an entity or relation multiple attributes of the same type is as simple as declaring them in an insert, and read queries automatically return all values.

1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
26
27
28
29
30
31
32
33

insert
  $john isa full-time-employee,
    has primary-email "john.doe@typedb.com",
    has email "j.doe@typedb.com",
    has email "john@typedb.com",
    has email "sales@typedb.com";
Globally Unique Attributes
Attributes are globally unique in TypeQL. If two entities each have an attribute with the same type and value, then they both have the same attribute instance. This allows for highly efficient data traversals, keeps disk usage low, and maintains a consistent model.

1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
26
27
28
29
30
31
32
33

insert
  $roadmap isa file,
    has path "/typedb/feature-roadmap.pdf",
    has confidentiality "public";
  $cloud isa repository,
    has name "typedb-cloud",
    has confidentiality "restricted";
  $sales isa database,
    has name "sales",
    has confidentiality "restricted";

match
  $rsrc has confidentiality $conf;
fetch
  $conf;
No Nulls
Unlike SQL and NoSQL modeling languages, TypeQL is entirely conceptual and does not need to implement nulls to store the absence of a value. Keep nulls out of your query results without compromising for a schema-less database.

1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
26
27
28
29
30
31
32
33

insert
  $john isa user, has full-name "John Doe";
  $david isa user, has email "david@typedb.com";

match
  $user isa user;
fetch
  $user: full-name, email;

# JSON output:
[{
    "user": {
        "type": { "root": "entity", "label": "user" },
        "full-name": [
            { "value": "John Doe", "value_type": "string", "type": { "root": "attribute", "label": "full-name" } }
        ],
        "email": []
    }
}, {
    "user": {
        "type": { "root": "entity", "label": "user" },
        "full-name": [],
        "email": [
            { "value": "david@typedb.com", "value_type": "string", "type": { "root": "attribute", "label": "email" } }
        ]
    }
}]

Attribute Constraints
Define a key constraint on an attribute to make ownership of that attribute required and ensure a unique value. Alternatively, use a unique constraint instead to ensure uniqueness without requiring ownership. Apply regex constraints to string attributes to enforce defined patterns.

1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
26
27
28
29
30
31
32
33

define
  full-name sub attribute, value string;
  office-location sub attribute,
    value string,
    regex "^(London|Paris|Dublin)$";
  id sub attribute, value string;
  email sub id, regex "^(.+)@(\\S+)$";
  employee-id sub id;
  user sub entity,
    owns full-name,
    owns email @unique;
  employee sub user,
    owns employee-id @key,
    owns office-location;
Purely Abstract Attributes
3.0 Roadmap
Define abstract attribute types with no declared value type, and extend them to define subtypes with different value types. Easily retrieve attribute values of different types by querying the abstract supertype.

1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
26
27
28
29
30
31
32
33
34
35

define
  id sub attribute, abstract;
  email sub id, value string;
  employee-id sub id, value long;
  path sub id, value string;
  user sub entity, owns email;
  employee sub user, owns employee-id;
  resource sub entity, abstract, owns id;
  file sub resource, owns path as id;

match
  $ent isa entity;
fetch
  $ent: id;

[{
    "ent": {
        "type": { "root": "entity", "label": "employee" },
        "id": [
            { "value": "francois@typedb.com", "value_type": "string", "type": { "root": "attribute", "label": "email" } },
            { "value": 184, "value_type": "long", "type": { "root": "attribute", "label": "employee-id" } }
        ]
    }
},{
    "ent": {
        "type": { "root": "entity", "label": "file" },
        "id": [
            { "value": "/typedb/upcoming-features.pdf", "value_type": "string", "type": { "root": "attribute", "label": "path" } }
        ]
    }
}]

Compound Value Types
3.0 Roadmap
Define compound value types for your attributes constructed from primitive types.



The theory of TypeQL: pioneering typeful query languages
TypeQL is directly built on the principles of modern programming language theory, which distill how we intuitively interact with computers using simple, yet formal, structures: types.

Dr. Christoph Dorn

Head of Research, TypeDB
March 25, 2024

TypeQL: A Type-Theoretic & Polymorphic Query Language, C. Dorn and H. Pribadi. Accepted for publication at ACM SIGMOD/PODS 2024 — honored with the Best Newcomer Award. Download PDF
Types for databases
Despite breaking with the traditions of long-established database query languages, TypeQL often feels deeply familiar even to first-time users of the language—this is because TypeQL is directly build on the principles of modern programming language theory which distill how we intuitively interact with computers using simple, yet powerful, structures: types. To quote from Harper’s 2012 book on the “Practical Foundations for programming languages”:

Types are the central organizing principle of the theory of programming languages. Language features are manifestations of type structure. The syntax of a language is governed by the constructs that define its types, and its semantics is determined by the interactions among those constructs. The soundness of a language design—the absence of ill-defined programs—follows naturally.

R. Harper
TypeQL is not alone in its mission of bringing the theory of types and the practice of industrial-strength languages together—typeful languages (a term coined by L. Cardelli) are trending. Types enable high-level, declarative constructions of programs using subtyping and polymorphism; they add regularity to languages and thereby clarify many programming issues long before they arise; and they are backed by a rigorous mathematical theory which accommodates low-level optimizations. This balance enables modern typeful programming languages (like Rust, OCaml, Haskell) to be fully-featured and performant languages, while at the same time bringing a maximal degree of declarativity and safety. The requirement of having to be precise about declaring the types in our code is a small price to pay for knowing “for sure” that our successfully type-checked program will stick precisely to the structure that we declared for it.

The theory and practice of TypeQL
Database languages have, so far, benefitted very little from the progress towards performant, high-level declarative languages based on types, neither in science nor in industry. TypeQL, the query language of our database TypeDB, aims to finally bring the key benefits of typeful programming languages to databases. After some intense research in our lab last year, the theory synthesizing typeful programming and database languages is now written out in detail in our most recent paper, which brings together many interesting topics from classical database theory and modern programming language theory—here it is:

“TypeQL: A Type-Theoretic and Polymorphic Query Language”, C. Dorn & H. Pribadi, Download PDF
(final version to be published in Proceedings of the ACM on Management of Data)

The paper explores a novel way of integrating typeful programming with performant database design, promoting traditional relations to so-called dependent types. This key step is based on a deep correspondence of classical logic and modern type theory known as the Propositions as Types paradigm. To quote from Wadler’s same-named paper:

Such a synthesis is offered by the principle of Propositions as Types, which links logic to computation. At first sight it appears to be a simple coincidence—almost a pun—but it turns out to be remarkably robust, inspiring the design of automated proof assistants and programming languages, and continuing to influence the forefronts of computing.

P. Wadler
In our paper, we evolve this fundamental principle further: we turn Propositions as Types into Queries as Types. This means that in TypeQL the user constructs types in order to formulate queries—of course, all this happens “under the hood”, packaged into TypeQL’s near-natural query language. The Queries as Types paradigm is where TypeQL strongly differs from existing QL paradigms:

Traditionally, database language have taken a somewhat more algebraic (or operational) viewpoint: for example, in SQL queries boil down sequences of operations that transform tables into other tables.
This similarly applies to prominent document database query languages, which operate on documents through “aggregation pipelines”.
Purely declarative, pattern-based approaches do exist, for example, in the realm of graph databases, but all existing approaches lack a sophisticated type system.
The PERA model
TypeQL is underpinned by powerful type system, which includes the expected key components of a typeful programming language such as subtyping and polymorphism (note that in TypeQL-lingo we speak of ‘interfaces’ where others may speak of ‘typeclasses’ or ‘traits’), but adapts these components directly to the setting of databases. Indeed, in databases, language cannot be overly complicated to avoid convoluting storage and retrieval of data, and so TypeQL’s type system breaks down its data-storing types down into only three key kinds:

Independent types that hold unique object identifiers, a.k.a. entities,
Dependent types that hold unique object identifiers, a.k.a. relations,
Independent types that hold literal values, a.k.a. independent attributes,
Dependent types that hold literal values, a.k.a. dependent attributes.
The resulting data model of TypeQL is called the PERA model, the polymorphic entity-relation-attribute model, and in our paper we show that the model is straight-forwardly described in the framework of type theory. Its simple ingredients combine to yield highly expressive model, unifying core aspects of (essentially all!) existing popular data models. This highlights a central and important aspect of our work: the PERA model is a unifying generalization of existing database paradigms—for the interested reader, we illustrate how this unification works with a range of detailed examples in Appendix A of our paper.

Epilogue: what’s next?
Our terminology of “entities”, “relations”, and “attributes” is, of course, a direct reflection of classical conceptual entity-relationship modeling—importantly, we view these concepts through a fresh, purely type-theoretic lens, which highlights an interesting convergence of classical, natural-language inspired thinking in databases and the modern theoretical framework of types. In fact, as we mention in our paper, this convergence goes even further: dependent types and subtypes mix very well, giving rise to a new type system feature which we call type functions that neatly generalizes Datalog-like reasoning. This, too, is an exciting contribution to database language theory—and you can expect to hear more about this idea soon!

More generally, as computer scientists, we are excited by the potential of typeful database programming for shedding new light on a plethora of open questions and recent scientific work concerning database, knowledge representation, and reasoning systems, including, for example:

Algorithms for efficient incremental view maintenance for rich query languages and reasoning systems,
Building complex real-world database benchmarks and that make use of the semantic expressivity of types,
Integrating neural and symbolic AI methods for information retrieval.
… and more! If these topics sounds interesting to you, don’t hesitate to be in touch.


What it means to be more strongly-typed than SQL and NoSQL
Learn about how the role of types in TypeDB is conceived in a fundamentally more powerful way than in other databases.

Dr. Christoph Dorn

Head of Research, TypeDB
November 8, 2023

Unlike existing database paradigms, TypeDB is designed based on modern ideas from type theory. If you want to learn how this works in detail, you may be interested in our article on type-theoretic databases in our learning section. In this post, we will discuss a crucial difference between TypeDB and other database paradigms, which is a direct result of these type-theoretic foundations of TypeDB. But don’t worry, we won’t assume any familiarity with type theory and will keep our discussion as high level as possible!

As a warm-up we will give a brief overview of various database paradigms and how these relate and organize. We then recall and discuss some of the key ideas from type theory and conceptual modeling that led to the design of TypeDB. Finally, this will set the stage for understanding our main claim in this post: that TypeDB is more strongly-typed than other popular databases!

A common language for data models
A big challenge in the field of database design is the large variety of data that we encounter on a daily basis. For this reason, many different data models, each with their own specific modeling and querying paradigms, have emerged over the past decades. Among the most prominent such models, one often finds the following mentioned:

The relational model. In the relational model we group data into tuples of relations, which can then be queried by a set of basic operations that manipulate relations. SQL is a query language standard implementing this paradigm, and is in many ways extending the original expressive strength of the model.
The triplestore model. The triplestore (or RDF) data model is based on the idea of storing representations of natural language statements of form “subject-predicate-object”. The dominant query language, SPARQL, takes much inspiration from SQL… after all, triples are just specific relations.
The graph model. Thinking about triples as the edges of a graph, the graph model conceptually extends the triplestore model by many useful graph operations, including e.g. transitive graph closures which cannot be easily expressed in standard SQL (as a trade-off, the graph model usually drops direct support of other powerful features of triplestore, like iterated reification).
The key/value model. The retrieval of values by keys is among the simplest database paradigms and doesn’t really comprise an interesting ‘data model’ in itself (i.e. a schematic organization of data). It is nonetheless pervasive in many different data storage systems: for instance, in vector databases we can query for approximate value vectors by key vectors relative to a pre-defined embedding map.
The document model. The document model extends the simple storage of key/value pairs by allowing for key/value mappings to themselves become values associated to a key. The result are data formats like XML or JSON, and these are implemented by several popular database.
TypeDB falls into none of the above categories: instead, it is based on its own “polymorphic conceptual” data model that, in particular, is meant to provide a common generalization of many of the above models. (Note: this stands in contrast to existing “multi-model” approaches, in which multiple different data models are implemented in parallel.) Indeed, conceptual data models are among the most expressive, high-level data models, and they often provide numerous ways of describing how data relates and is structured. For this reason, conceptual data models still feature centrally in database theory and are often considered a “very important phase in designing a successful database application” [Chapter 3, “Fundamentals of database systems”, 2016]. Famous examples of conceptual data models include Chen’s entity-relation model (ER model), and Abiteboul-Hull’s generic semantic model (GSM).

Unfortunately, a frequent issue with high-level conceptual data models is their lack of practical mathematical formalizations. In the reliability-sensitive field of database theory we need a workable theory to make correctness guarantees for query planning, optimization and transactionality (in contrast, lack of careful theoretical verification can lead to serious issues that frequently affect NoSQL databases in particular). This is where type theory comes into play, a sub-field of mathematical logic. TypeDB is built around the realization that mathematical ideas central to type theory are very well-suited to make precise the informal notions from classical conceptual data modeling. Along this line of thought, the topic of “type-theoretic databases” has recently gained much traction in both academia and industry.

So: what is exactly is the role of type theory for TypeDB, and how does it relate to conceptual data models more generally?

From variables to type theory
TypeDB’s design philosophy centers around the variabilization of natural language. Consider the sentence:

Today I ate an apple.
A variabilized version of this statement could, for instance, read:

Today I ate an $x.
Variables represent information unknown to us. However, the space of all information is intractably big, and so it makes sense to constrain the unknown further: this is the purpose of types. Together, variables and types make up the glue of much of mathematics: this begins, for instance, with elementary equational statements such as “solve x^n + y^n = z^n for positive integers x, y, z, n where n > 2”: here, both the constraints “positive integer” and “> 2” describe the types of the variables at issue.

In TypeDB, variables and types fulfill a very similar purpose: we use types to enable the user to specify which operations are possible (for instance, which types can play which roles in other types, or which types may have which attributes associated to them), and then use composite type constraints to build queries and reason about variables. Importantly, for the purposes of efficient data modeling we found that we do not need the full power of existing type theories: for example, much of every day reasoning happens at the level of first-order functional dependencies and so higher-order functions are absent in TypeDB. These choices guarantee optimizability and performance of the database. The following slogan summarizes our approach:

TypeDB follows a type-theoretic conceptual data model enhanced with type polymorphism.

TypeDB’s type theoretical conceptual modeling primitives
Let us briefly go into more detail about what me mean by designing a language close to the “classical primitives of conceptual data modeling” while at the same time taking inspiration from type theory. Our main conceptual data model, for reference, will be Chen’s entity-relation model. Common primitives of ER-modeling include, for instance, entitites, relations, and attributes. One way to motivate these primitives is by their usage in natural language. Importantly, however, they may alternatively be motivated from a purely type-theoretic perspective as well.

Entity types are a class of types which (as types) do not depend on any other types, and whose terms are non-composite expressions (or ‘structureless’ constants, if you wish). Entities must therefore be identified by the information that they are connected to, i.e. by their relations to other data and by their attribute values.
Relation types are, like entity types, types whose terms are non-composite expressions. However, unlike entity types, they may depend on other types. The type marriage(s) of $x and $y is an example very much in the spirit of our earlier discussion of variabilization: the variables $x and $y are unknowns that the type of marriage(s) depends on. The functional programmers among us may know that binary relations are generalized by so-called profunctors (as used e.g. in Haskell), and this is precisely the right way to think about relation types in TypeDB (generalized to the n-ary case, n > 0).
Value types, unlike entities or relations, have structure. For example, numbers have structure (e.g. addition is a structure, making e.g. 3 = 2 + 1) and so do strings: a term 'abc' in the type of strings is precisely the composite of its individual characters. The presence of structure means that value types have meaningful (namely, structure-preserving) interpretations across different systems: put plainly, the concept of numbers makes sense across many different systems, and no one is surprised that most programming languages support it.
Attribute types, like relations, are dependent types but their terms are required to be values (i.e. terms sourced from value types); as an example, consider the type names of $x. (Note, while theoretically we could have attributes depending on multiple other types, like e.g. the binary attribute measured distance between $x and $y, in TypeDB we made the choice of letting attributes only depend on at most one type, called the attribute’s owner: this avoids ambiguity, since n-ary attributes may also be modeled as attributes of n-ary relations, say, a length attribute of a binary relation path between $x and $y.)
There are many other aspects of conceptual modeling that can be type-theoretically addressed in a similar way (including functional dependencies, cardinality constraints, key attributes, and many more). Moreover, and importantly, the query language TypeQL of TypeDB also adds additional powerful features that are motivated not by the theory of conceptual data models but from a point of view of type theory: these, for example, include formal modes of data deduction as well as type-polymorphic querying, which we will now discuss in more detail.

Everything has a type
The term strongly-typed is, in general, not very precisely defined. Usually, one finds definitions along the following lines: a language is strongly typed if at the time of compilation (or interpretation) each expression, i.e. each variable or composite expression, is given a well-defined type. One issue (of several) with this definition is the notion of expressions. For example, while the expression if A then True else False would likely count as a typable expression (you may agree the type is Boolean), the expression while A do B is harder to give a type to, due to its fundamentally imperative nature. In contrast, in the world of type theory (and this also extends to functional programming languages) essentially everything can be understood to have a type, even entire programs. While we are on this topic, here is one of our favorite quotes (by Ulrik Buchholtz, professor in functional programming at Nottingham University).

To be is to be the element of a type.

Ulrik Buchholtz
Following this mantra, instead of our earlier definition, one may informally define “strong(er) typing” to mean the following: we say a language is (more) strongly-typed if (more of) its syntactic components can be given types, either implicitly or explicitly. This interpretation of the term ‘strongly-typed’ is, in particular, closely related to the usage of the word in the context of interpreting one system in another type system.

Hold on for a second, everything has a type? What about types, do types have types? Yes, even types have types; in fact, this is a crucial feature of modern type theories allowing for mathematics to ‘make statements about itself’. And, for us in TypeQL, the same holds true. By allowing for essentially all components of our languages to be variabilized, we obtain a much more expressive class of queries that can ask questions about the database structure itself. For example, consider the statement:

$event is a marriage between wife Andrea and wife Beatrice.
In TypeQL, all parts of this statement can be variabilized (and in each case this turns the statement into an appropriate query); for instance we could variabilize the above as:

$event is a marriage between $role Andrea and wife Beatrice.
$event is a $relation between $role1 Andrea and $role2 Beatrice.
$event is a $relation between $role1 $person1 and $role2 $person2.
(As an aside: while the above are variabilized statements in natural language, you will find that the actual TypeQL code doesn’t look that different at all!)

In contrast to the above, type-theoretic design principles play a rather sub-ordinate role in most other existing data models and their query languages. For instance, in the relational model, relation tuples (i.e. rows) are given types, namely the “type of their relation” (i.e. of their table). In particular, unary tuples (i.e. rows with a single column) are usually typed with a datatype specified for that column. So, if we only care about relation tuples as expressions then it is true that SQL qualifies as a ‘strongly-typed’ language. But there are, of course, many other components to SQL as a language, and most of those components cannot be usefully treated as typed. Thus, they cannot be variabilized or queried for. As a example related to the above, we cannot have variables that represent columns in tables themselves, and so we cannot query, say, for an attribute that fulfils specific conditions:

Andrea has an $attribute that contains the string '@typedb.com

To repeat: in SQL we cannot write a query of the above form, which would have to return columns of, say, some table person with row Andrea. This is one of several ways in which TypeQL is strictly more expressive than SQL. Similar remarks apply to most other data models. Of course, one should always be careful to not compare apples and oranges, and often systems are designed for very domain-specific purposes without the goal of creating a highly generalizable query language. But importantly, the approach taken by TypeQL outlined above, makes it possible for many other data models to be naturally subsumed in it.

Conclusion
This concludes our brief discussion of the “very strong” typing in TypeQL. As a query language, TypeQL aims to strike a new powerful balance between intuivity, generalizability, and optimizability, and this must include the ability to variabilize types. We built TypeQL firmly on the principle: everything has a type, and so everything can be a variable.


Why We Need a Polymorphic Database
Subscribe to lectures
Download slides

Databases have come a long way since the navigational databases of the 1960s. The relational, document, and graph database paradigms have each profoundly impacted the way we store and query data, but many fundamental engineering challenges remain. Why is object-relational mismatch still a problem after 50 years? Why do we need ORMs to manage our data models for us? Why do queries need to be updated when the data model is extended, even if the question being asked remains the same?

Each successive database paradigm has only implemented workarounds to these problems without addressing the underlying cause: they cannot interpret declarative polymorphic queries. Programming languages have continuously become more powerful and declarative as they have evolved, but database query languages have not significantly advanced beyond SQL. This has left databases unable to express many of the OOP features that we easily take for granted, like abstraction, inheritance, and polymorphism.

In this lecture, we’ll examine the historical context and design philosophies behind the relational, document, and graph database paradigms to understand their strengths and weaknesses. We’ll look at the different strategies that database engineers employ to work around translating polymorphism from their object models. We’ll explore a polymorphic object model for a simple filesystem and see how the lack of expressivity inherent in current databases leads to fundamentally brittle application architectures. Finally, we’ll attempt to answer the question: why do we need a polymorphic database?

Join this lecture and learn more about:

The strengths and weaknesses of current database paradigms.
How databases engineers work around polymorphism in data models.
How current databases lead to fundamentally brittle application architectures.
Lecture materials:

GitHub repo to file system code example
https://github.com/typedb/filesystem-example


TypeDB: a New Kind of Database
TypeDB is a new kind of database with a polymorphic conceptual data model, a strong subtyping system, a symbolic reasoning engine, and a type-theoretic language: TypeQL. These are features not normally associated with a database, and TypeDB is a novel technology in the database space, solving several key challenges.

This article series breaks down the above statement down and explores each of these core features in detail. To begin with, a schema for a simple filesystem is presented. It illustrates how data domains can be modeled naturally by using the conceptual PERA model, including the occurrence of polymorphism and complex relation types. The expressive power and elegance of the type-theoretic query language TypeQL is then demonstrated by presenting several declarative queries on that schema, featuring complete polymorphic querying capabilities and type variablization. The strong type system that enables type inference and semantic validation is then examined to understand how declarative polymorphic querying is achieved. Finally, one of the most useful outcomes of the type system is showcased: TypeDB’s built-in symbolic reasoner.

Conceptual data model
TypeDB uses the polymorphic entity-relation-attribute (PERA) model (Dorn, Pribadi, 2024) for schemas and data. It is an extension of the entity-relationship (ER) model (Chen, 1976), which is the most widely used tool for designing conceptual data models due to its elegant simplicity and expressive power. Normally, the conceptual model is only a starting point, and it must be translated into a logical model that meets the modeling capabilities of the database system. As TypeDB uses the PERA model, any ER model can be directly implemented without translation. Likewise, any logical data model derived from an ER model can also be directly implemented, enabling easy migration of data from other database paradigms.

The PERA model allows us to make use of powerful polymorphic features, some examples in the schema excerpt below being:

Inheritance: admin is a subtype of user, so it inherits all of the supertype’s capabilities: any attributes it owns, and any roles it playes. When we give user more capabilities later on, they will be inherited as well.
Interfaces: Both user-group and resource own created-timestamp. This is possible because attribute ownerships and relation roles are interfaces that can be independently implemented by types with no common supertype.
Abstraction: resource is abstract. It can only be instantiated through one of its non-abstract subtypes, file and directory.
Overriding: file and directory both own path, a subtype of id. This specific implementation overrides the ownership of id by their supertype resource.
define

user sub entity,
    owns email,
    owns password-hash,
    owns created-timestamp,
    owns active,
    plays resource-ownership:resource-owner;

admin sub user,
    plays group-ownership:group-owner;

user-group sub entity,
    owns name,
    owns created-timestamp,
    plays group-ownership:group,
    plays resource-ownership:resource-owner;

resource sub entity,
    abstract,
    owns id,
    owns created-timestamp,
    owns modified-timestamp,
    plays resource-ownership:resource;

file sub resource,
    owns path as id;

directory sub resource,
    owns path as id;

ownership sub relation,
    abstract,
    relates owned,
    relates owner;

group-ownership sub ownership,
    relates group as owned,
    relates group-owner as owner;

resource-ownership sub ownership,
    relates resource as owned,
    relates resource-owner as owner;

id sub attribute, abstract, value string;
email sub id;
name sub id;
path sub id;
password-hash sub attribute, value string;
event-timestamp sub attribute, abstract, value datetime;
created-timestamp sub event-timestamp;
modified-timestamp sub event-timestamp;
active sub attribute, value boolean;
A database serves as a source-of-truth for an organisation’s data. For this reason, it is essential that the database model represents the desired business logic as closely as possible. Normally, the conceptual data model must be translated into the database’s logical model. This results in object model mismatch, and exposes data to silent corruption by semantic integrity loss. Because TypeDB directly implements the conceptual PERA model as its logical model, there is no mismatch with application models. This allows polymorphic constraints between types to be accurately expressed, ensuring semantic integrity of data.

You can read the full article to learn more about the conceptual data model of TypeDB.

Type-theoretic query language
TypeQL is the type-theoretic query language of TypeDB. One of the central design principles of the language is:

Everything has a type, and so everything can be a variable.

This allows for highly expressive querying power beyond the capabilities of other modern database paradigms. In particular, it allows for declarative polymorphic querying, which is not possible in non-polymorphic databases. We can use three fundamental types of polymorphism in our queries: inheritance polymorphism, interface polymorphism, and parametric polymorphism.

In the following example query, we use inheritance polymorphism to list the ID and event timestamps of all resources. Inheritance polymorphism allows us to declaratively query a type and retrieve instances of that type and all of its subtypes, and we retrieve instances of the subtypes of resource: files and directories. In fact, we will not get any results that are specifically of type resource as the type is abstract. Inheritance polymorphism also affects the attributes returned. The IDs retrieved are paths because path is a subtype of id, and the event timestamps retrieved are creation and modification timestamps because created-timestamp and modified-timestamp are subtypes of event timestamp. Here, the polymorphic constraints on the entity and its attributes have been combined to produce the result set, without having to use any special syntax to do so!

match
$resource isa resource;
fetch
$resource: id, event-timestamp;
{
    "resource": {
        "event-timestamp": [
            { "value": "2023-08-08T11:57:54.000", "value_type": "datetime", "type": { "label": "modified-timestamp", "root": "attribute" } },
            { "value": "2023-08-13T13:16:10.000", "value_type": "datetime", "type": { "label": "modified-timestamp", "root": "attribute" } },
            { "value": "2023-10-10T13:22:37.000", "value_type": "datetime", "type": { "label": "modified-timestamp", "root": "attribute" } },
            { "value": "2023-10-10T13:39:19.000", "value_type": "datetime", "type": { "label": "modified-timestamp", "root": "attribute" } },
            { "value": "2023-11-29T09:17:47.000", "value_type": "datetime", "type": { "label": "modified-timestamp", "root": "attribute" } },
            { "value": "2023-06-14T22:44:22.000", "value_type": "datetime", "type": { "label": "created-timestamp", "root": "attribute" } }
        ],
        "id": [ { "value": "/vaticle/research/prototypes/nlp-query-generator.py", "value_type": "string", "type": { "label": "path", "root": "attribute" } } ],
        "type": { "label": "file", "root": "entity" }
    }
}
{
    "resource": {
        "event-timestamp": [
            { "value": "2023-06-22T11:36:20.000", "value_type": "datetime", "type": { "label": "modified-timestamp", "root": "attribute" } },
            { "value": "2023-06-29T12:16:33.000", "value_type": "datetime", "type": { "label": "modified-timestamp", "root": "attribute" } },
            { "value": "2023-07-26T12:33:37.000", "value_type": "datetime", "type": { "label": "modified-timestamp", "root": "attribute" } },
            { "value": "2023-01-31T19:39:32.000", "value_type": "datetime", "type": { "label": "created-timestamp", "root": "attribute" } }
        ],
        "id": [ { "value": "/vaticle/research/prototypes/root-cause-analyzer.py", "value_type": "string", "type": { "label": "path", "root": "attribute" } } ],
        "type": { "label": "file", "root": "entity" }
    }
}
{
    "resource": {
        "event-timestamp": [
            { "value": "2023-02-15T09:13:55.000", "value_type": "datetime", "type": { "label": "modified-timestamp", "root": "attribute" } },
            { "value": "2023-03-25T12:11:15.000", "value_type": "datetime", "type": { "label": "modified-timestamp", "root": "attribute" } },
            { "value": "2023-06-02T06:17:54.000", "value_type": "datetime", "type": { "label": "modified-timestamp", "root": "attribute" } },
            { "value": "2023-12-04T23:07:09.000", "value_type": "datetime", "type": { "label": "modified-timestamp", "root": "attribute" } },
            { "value": "2023-01-28T09:16:24.000", "value_type": "datetime", "type": { "label": "created-timestamp", "root": "attribute" } }
        ],
        "id": [ { "value": "/vaticle/engineering/tools/performance-profiler.rs", "value_type": "string", "type": { "label": "path", "root": "attribute" } } ],
        "type": { "label": "file", "root": "entity" }
    }
}
{
    "resource": {
        "event-timestamp": [
            { "value": "2023-11-23T07:05:18.000", "value_type": "datetime", "type": { "label": "modified-timestamp", "root": "attribute" } },
            { "value": "2023-10-01T01:46:23.000", "value_type": "datetime", "type": { "label": "created-timestamp", "root": "attribute" } }
        ],
        "id": [ { "value": "/vaticle/engineering/projects/typedb-3.0", "value_type": "string", "type": { "label": "path", "root": "attribute" } } ],
        "type": { "label": "directory", "root": "entity" }
    }
}
{
    "resource": {
        "event-timestamp": [
            { "value": "2023-10-20T13:24:19.000", "value_type": "datetime", "type": { "label": "modified-timestamp", "root": "attribute" } },
            { "value": "2023-10-22T12:22:51.000", "value_type": "datetime", "type": { "label": "modified-timestamp", "root": "attribute" } },
            { "value": "2023-12-01T03:58:22.000", "value_type": "datetime", "type": { "label": "modified-timestamp", "root": "attribute" } },
            { "value": "2023-12-28T02:00:04.000", "value_type": "datetime", "type": { "label": "modified-timestamp", "root": "attribute" } },
            { "value": "2023-03-13T14:25:07.000", "value_type": "datetime", "type": { "label": "created-timestamp", "root": "attribute" } }
        ],
        "id": [ { "value": "/vaticle/engineering/projects/typedb-cloud-beta", "value_type": "string", "type": { "label": "path", "root": "attribute" } } ],
        "type": { "label": "directory", "root": "entity" }
    }
}
TypeQL’s declarative polymorphic queries allow us to easy extend data models without refactoring queries. When we leverage inheritance polymorphism, we do not have to enumerate the subtypes of the supertype being queried. Because the types are never explicitly listed, queries do not have to be modified to include newly added types or exclude previously removed types. This is very different to other database paradigms where such enumeration would normally be necessary.

You can read the full article to learn more about the type-theoretic query language of TypeDB.

Strong type system
The backbone of TypeDB is its strong type system, which powers its declarative polymorphic queries and semantic data validation. The type system is managed by the type-inference engine, which resolves every query against the schema to determine the possible return types. It also performs semantic validation, preventing nonsensical queries from being executed.

To build the set of return types for the above query, TypeDB identifies the constraints it comprises. The pattern in the match clause tells us that $resource has the type resource, indicating that the type of $resource must be either resource itself or one of its subtypes. The type resource itself is abstract, and so is excluded. The fetch clause then tells us that we would like to retrieve the id and event-timestamp attributes of $resource. The return types of both attributes have dependencies on the resolved type of $resource, so we can identify the return types of the attributes based on the attribute ownerships in the schema. The actual return types of the query can be enumerated as rows in the following table.

$resource	$resource: id	$resource: event-timestamp
file	path	created-timestamp
file	path	modified-timestamp
directory	path	created-timestamp
directory	path	modified-timestamp
repository	name	created-timestamp
repository	name	modified-timestamp
This is roughly how TypeDB’s type-inference engine works to resolve the possible return types of a query. The return types are then supplied to the query planner, which searches for instances of the those types in the data. If a query has no possible sets of return types, then it is not permitted by the schema and thus semantically invalid! TypeDB is designed with polymorphism as a central feature. By combining a conceptual data model with a type-theoretic query language, the type-inference engine is able to resolve declarative polymorphic queries and identify semantically invalid ones.

You can read the full article to learn more about the strong type system of TypeDB.

Symbol reasoning engine
In TypeDB, symbolic reasoning takes the form of rule inference, which allows the database to generate new facts based on existing data and user-defined rules. Resolution of rules is managed by the rule-inference engine. The data created by rules is generated at query-time and held in memory. This means that they will always reflect the most recent state of the schema and data when the query is run, so we don’t have to worry about stale or inconsistent data, and disk space is saved. Once we close the transaction, the rule-inference cache is cleared and the resources are released. Rule inference has a number of powerful use cases, ranging from creating convenient abstractions for patterns used across multiple queries, to capturing complex business logic from the data domain.

In the above data model, we’ll often need to query for the last modification timestamp of resources. Rather than searching through the modification timestamps each time, we can generate the attributes using the following rule. Rules use the same pattern syntax as queries, so they can make use of polymorphic patterns. In this rule, we use inheritance polymorphism to assign last-modified timstamps to all resources via their supertype resource. Rules also undergo semantic validation to ensure the integrity of generated data.

define

last-modified sub attribute, value datetime;
resource owns last-modified;

rule resource-last-modified:
    when {
        $resource isa resource, has modified-timestamp $last-modified;
        not {
            $resource has modified-timestamp $other-modified;
            $other-modified > $last-modified;
        };
        # Copy the value of $last-modified
        ?timestamp = $last-modified;
    } then {
        # Generate a new attribute with the same value
        $resource has last-modified ?timestamp;
    };
With the rule defined, we can easily query the new attributes. We do not have to specify which rules to use, as the rule-inference engine will find and apply all applicable rules in the schema.

match
$resource isa resource, has last-modified $last-modified;
fetch
$resource: id;
$last-modified;
The new attribute type can be used in any other query too, so we don’t have to repeat the full pattern anywhere outside of the rule. This also means that if we want to change how the last modification timestamp is determined, we only have to change it in the rule, which serves as a single source of truth.

You can read the full article to learn more about the symbolic reasoning engine of TypeDB.

Summary
TypeDB’s unique features as a polymorphic database allow it to elegantly describe the polymorphism inherent in most application models. This is possible because of its core features, which are designed with polymorphism foremost in mind:

The conceptual data model enables the complete elimination of mismatch with object models while enforcing the semantic integrity of inserted data.
The type-theoretic query language permits the construction of declarative queries encompassing inheritance, interface, and parametric polymorphism.
The strong type system allows the execution of declarative polymorphic queries by validating and resolving those queries against the schema.
The symbolic reasoner captures the logic of the data domain through rules, which generate new facts in a consistent and up-to-date manner.
In addition to these core elements, TypeDB incorporates many other features required of modern databases, such as asynchronous query execution and resilient clustering. A complete list of TypeDB’s features would be too long for an article, but a high-level summary can be found on the features page.

Share this article
TypeDB Newsletter
Stay up to date with the latest TypeDB announcements and events.

Subscribe to Newsletter
Further Learning


The Symbolic Reasoning Engine of TypeDB
The conceptual model, type-theoretic language, and strong type system of TypeDB come together to enable symbolic reasoning. In TypeDB, reasoning takes the form of rule inference, which allows the database to generate new facts based on existing data and user-defined rules. Resolution of rules is managed by the rule-inference engine. The data created by rules is generated at query-time and held in memory. This means that they will always reflect the most recent state of the schema and data when the query is run, so we don’t have to worry about stale or inconsistent data, and disk space is saved. Once we close the transaction, the rule-inference cache is cleared and the resources are released.

Rule inference has a number of powerful use cases, ranging from creating convenient abstractions for patterns used across multiple queries, to capturing complex business logic from the data domain. In this article, we’ll examine some of the ways we can use rule inference to simplify and enhance database operations. We’ll begin with an example of a single rule, then see how we can combine them in powerful ways.

This article uses an example data model and queries for a simple filesystem based on a discretionary access control (DAC) permission system. In the DAC framework, all objects (for instance files, directories, and user groups) have owners, and permissions on an object are granted to other users by its owner. The schema, dataset, and queries can all be found on GitHub.

Simple rules
In the following query, we retrieve the most recent modification timestamp for each resource without using rule inference.

match
$resource isa resource, has modified-timestamp $last-modified;
not {
    $resource has modified-timestamp $other-modified;
    $other-modified > $last-modified;
};
fetch
$resource: id;
$last-modified;
{
    "resource": {
        "id": [ { "value": "/vaticle/engineering/projects/typedb-3.0/traversal-engine.rs", "value_type": "string", "type": { "label": "path", "root": "attribute" } } ],
        "type": { "label": "file", "root": "entity" }
    },
    "last-modified": { "value": "2023-12-09T14:36:26.000", "value_type": "datetime", "type": { "label": "modified-timestamp", "root": "attribute" } }
}
{
    "resource": {
        "id": [ { "value": "/vaticle/engineering/projects/typedb-cloud-beta/user-guide.md", "value_type": "string", "type": { "label": "path", "root": "attribute" } } ],
        "type": { "label": "file", "root": "entity" }
    },
    "last-modified": { "value": "2023-12-06T07:15:09.000", "value_type": "datetime", "type": { "label": "modified-timestamp", "root": "attribute" } }
}
{
    "resource": {
        "id": [ { "value": "/vaticle/engineering/projects/typedb-3.0/technical-specification.md", "value_type": "string", "type": { "label": "path", "root": "attribute" } } ],
        "type": { "label": "file", "root": "entity" }
    },
    "last-modified": { "value": "2023-11-24T14:06:36.000", "value_type": "datetime", "type": { "label": "modified-timestamp", "root": "attribute" } }
}
{
    "resource": {
        "id": [ { "value": "/vaticle/engineering/projects/typedb-3.0/release-notes.md", "value_type": "string", "type": { "label": "path", "root": "attribute" } } ],
        "type": { "label": "file", "root": "entity" }
    },
    "last-modified": { "value": "2023-12-17T22:31:07.000", "value_type": "datetime", "type": { "label": "modified-timestamp", "root": "attribute" } }
}
{
    "resource": {
        "id": [ { "value": "/vaticle/engineering/projects/typedb-cloud-beta/user-manager.rs", "value_type": "string", "type": { "label": "path", "root": "attribute" } } ],
        "type": { "label": "file", "root": "entity" }
    },
    "last-modified": { "value": "2023-12-12T03:45:35.000", "value_type": "datetime", "type": { "label": "modified-timestamp", "root": "attribute" } }
}
It’s not a complex query, but checking for later modification timestamps is a bit cumbersome. We’ll likely need to query last modification timestamps as part of a lot of larger queries, so this query pattern will need to be repeated many times across our codebase. Rather than searching through the modification timestamps each time, it would be better if we store the most recent timestamp in a way we can access it more conveniently. We could separately insert a special last-modified timestamp on every resource, but then we’d need to manually update it whenever we add a new modified-timestamp. This could lead to inconsistent data if we’re not careful. This situation is a perfect use case for rule-inference, which can ensure our data stays consistent. To begin with, we go ahead and define the new attribute with a Define query.

define

last-modified sub attribute, value datetime;
resource owns last-modified;
Next, we write a rule using the pattern from our original query and add it to our database, also with a Define query. Like types, rules are a core part of the schema.

define

rule resource-last-modified:
    when {
        # The original query pattern
        $resource isa resource, has modified-timestamp $last-modified;
        not {
            $resource has modified-timestamp $other-modified;
            $other-modified > $last-modified;
        };
        # Copy the value of $last-modified
        ?timestamp = $last-modified;
    } then {
        # Generate a new attribute with the same value
        $resource has last-modified ?timestamp;
    };
Rules use the same pattern syntax as queries, so they can make use of polymorphic patterns. In this rule, we use inheritance polymorphism to assign last-modified timstamps to all resources via their supertype resource. Rules also undergo semantic validation to ensure the integrity of generated data. With the rule defined, we can replace our original query for the most recent modified-timestamp with a simple query for last-modified. The results are identical to those before, except that that type field of $last-modified has changed from modified-timestamp to last-modified.

match
$resource isa resource, has last-modified $last-modified;
fetch
$resource: id;
$last-modified;
{
    "resource": {
        "id": [ { "value": "/vaticle/engineering/projects/typedb-3.0/traversal-engine.rs", "value_type": "string", "type": { "label": "path", "root": "attribute" } } ],
        "type": { "label": "file", "root": "entity" }
    },
    "last-modified": { "value": "2023-12-09T14:36:26.000", "value_type": "datetime", "type": { "label": "last-modified", "root": "attribute" } }
}
{
    "resource": {
        "id": [ { "value": "/vaticle/engineering/projects/typedb-cloud-beta/user-guide.md", "value_type": "string", "type": { "label": "path", "root": "attribute" } } ],
        "type": { "label": "file", "root": "entity" }
    },
    "last-modified": { "value": "2023-12-06T07:15:09.000", "value_type": "datetime", "type": { "label": "last-modified", "root": "attribute" } }
}
{
    "resource": {
        "id": [ { "value": "/vaticle/engineering/projects/typedb-3.0/technical-specification.md", "value_type": "string", "type": { "label": "path", "root": "attribute" } } ],
        "type": { "label": "file", "root": "entity" }
    },
    "last-modified": { "value": "2023-11-24T14:06:36.000", "value_type": "datetime", "type": { "label": "last-modified", "root": "attribute" } }
}
{
    "resource": {
        "id": [ { "value": "/vaticle/engineering/projects/typedb-3.0/release-notes.md", "value_type": "string", "type": { "label": "path", "root": "attribute" } } ],
        "type": { "label": "file", "root": "entity" }
    },
    "last-modified": { "value": "2023-12-17T22:31:07.000", "value_type": "datetime", "type": { "label": "last-modified", "root": "attribute" } }
}
{
    "resource": {
        "id": [ { "value": "/vaticle/engineering/projects/typedb-cloud-beta/user-manager.rs", "value_type": "string", "type": { "label": "path", "root": "attribute" } } ],
        "type": { "label": "file", "root": "entity" }
    },
    "last-modified": { "value": "2023-12-12T03:45:35.000", "value_type": "datetime", "type": { "label": "last-modified", "root": "attribute" } }
}
The new attribute type can be used in any other query too, so we don’t have to repeat the full pattern from the original query anywhere outside of the rule. This also means that if we want to change how the last modification timestamp is determined, we only have to change it in the rule, which serves as a single source of truth.

Rule branching
When used together, multiple rules can emulate very powerful logic, consistent with the way we naturally think about data. In the following rule, we check for resources that don’t have any modification timestamps, and generate last-modified attributes equal to the creation timestamps instead. This generates the same conclusion as the previous rule, so the two rules represent parallel branches of logic. As their conditions are mutually exclusive, only one last-modified attribute will be generated per resource.

define

rule implicit-resource-last-modified:
    when {
        $resource isa resource, has created-timestamp $created;
        not { $resource has modified-timestamp $modified; };
        ?timestamp = $created;
    } then {
        $resource has last-modified ?timestamp;
    };
When we query for last modification timestamps, we can continue to use the same query as before. We do not have to specify which rules to use, as the rule-inference engine will find all applicable rules in the schema and apply them in parallel.

match
$resource isa resource, has last-modified $last-modified;
fetch
$resource: id;
$last-modified;
Rule chaining
In addition to using branches of logic, rules can also be combined to form chains of logic. In the next rule, we generate modification timestamps for repositories equal to the creation timestamps of the commits on those repositories.

define

rule repository-modified-timestamps:
    when {
        $repository isa repository;
        (repository: $repository) isa commit, has created-timestamp $commit-created;
        ?timestamp = $commit-created;
    } then {
        $repository has modified-timestamp ?timestamp;
    };
The rule-inference engine uses a backward-chaining method to resolve rules. This rule generates a modification timestamp, and both the previous rules resource-last-modified and implicit-resource-last-modified search for modification timestamps. As a result, the modified-timestamp instances that it generates can be used to generate last-modified instances! Again, it is not necessary to specify which rules to use. The rule-inference engine will trigger any applicable rules in the correct order. If we query for the last modified timestamps of repositories, we now get the timestamps of the most recent commits on them.

match
$repository isa repository, has last-modified $last-modified;
fetch
$repository: id;
$last-modified;
{
    "repository": {
        "id": [ { "value": "typedb-cloud", "value_type": "string", "type": { "label": "name", "root": "attribute" } } ],
        "type": { "label": "repository", "root": "entity" }
    },
    "last-modified": { "value": "2023-12-13T01:05:03.000", "value_type": "datetime", "type": { "label": "last-modified", "root": "attribute" } }
}
{
    "repository": {
        "id": [ { "value": "typedb", "value_type": "string", "type": { "label": "name", "root": "attribute" } } ],
        "type": { "label": "repository", "root": "entity" }
    },
    "last-modified": { "value": "2023-08-19T02:08:58.000", "value_type": "datetime", "type": { "label": "last-modified", "root": "attribute" } }
}
Rule recursion
Finally, we’ll examine a special case of rule chaining that allows for recursive logic. For this example, we’ll move away from modification timestamps and focus on another part of the data model. Let’s consider the file type-theory.tex, and query the directories it is in.

match
$paper isa file, has path "/vaticle/research/papers/type-theory.tex";
$directory isa directory, has path $path;
(directory: $directory, directory-member: $paper) isa directory-membership;
fetch
$path;
{ "path": { "value": "/vaticle/research/papers", "value_type": "string", "type": { "label": "path", "root": "attribute" } } }
We only get one result, though logically the file is also in the directories /vaticle/research and /vaticle. We can see this by querying further up the directory structure.

match
$papers isa directory, has path "/vaticle/research/papers";
$directory isa directory, has path $path;
(directory: $directory, directory-member: $papers) isa directory-membership;
fetch
$path;
{ "path": { "value": "/vaticle/research", "value_type": "string", "type": { "label": "path", "root": "attribute" } } }
match
$research isa directory, has path "/vaticle/research";
$directory isa directory, has path $path;
(directory: $directory, directory-member: $research) isa directory-membership;
fetch
$path;
{ "path": { "value": "/vaticle", "value_type": "string", "type": { "label": "path", "root": "attribute" } } }
In application code, this would be an excellent use case for recursion, which would allow us to write a function that easily retrieves all of a file’s parent directories at once. We can do the same with rule chaining, by defining a rule that can trigger itself.

define

indirect-directory-membership sub directory-membership;

rule transitive-directory-memberships:
    when {
        (directory: $directory-1, directory-member: $directory-2) isa directory-membership;
        (directory: $directory-2, directory-member: $object) isa directory-membership;
    } then {
        (directory: $directory-1, directory-member: $object) isa indirect-directory-membership;
    };
When this rule is triggered, the rule-inference engine will search for instances of directory-membership between $directory-1 and $directory-2, and between $directory-2 and $object. As this rule can generate instances of indirect-directory-membership (which is a subtype of directory-membership) between those roleplayers, the rule will be triggered again! If we run the query again after adding this rule to the schema, we can see that the expected directory tree is correctly returned.

match
$paper isa file, has path "/vaticle/research/papers/type-theory.tex";
$directory isa directory, has path $path;
(directory: $directory, directory-member: $paper) isa directory-membership;
fetch
$path;
{ "path": { "value": "/vaticle/research/papers", "value_type": "string", "type": { "label": "path", "root": "attribute" } } }
{ "path": { "value": "/vaticle/research", "value_type": "string", "type": { "label": "path", "root": "attribute" } } }
{ "path": { "value": "/vaticle", "value_type": "string", "type": { "label": "path", "root": "attribute" } } }
While the rule doesn’t define an explicit base case, it terminates because the rule-inference engine will only generate each given data instance once. This means that rule inference is always guaranteed to terminate except in a few niche cases, such as using a recursive rule involving arithmetic to generate numeric attributes in an unbounded sequence. These cases do not arise in practical database design, but are a consequence of TypeQL’s Turing completeness.

Summary
These rules demonstrate the basic ways in which rules can be used, but they only scratch the surface of what is possible with rule inference. Some additional rules are included in the sample code for the interested reader.