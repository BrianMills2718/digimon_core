#!/usr/bin/env python3
"""Simple question answering based on entity types"""

import sys
from neo4j import GraphDatabase

def answer_question(question):
    driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "password"))
    
    question_lower = question.lower()
    
    with driver.session() as session:
        # Determine what type of entities to search for based on question
        if any(word in question_lower for word in ['organization', 'company', 'companies', 'corporation']):
            print("\n🏢 Organizations found in the document:\n")
            result = session.run("""
                MATCH (e:Entity:ORG)
                RETURN e.canonical_name as name, e.pagerank_score as score
                ORDER BY coalesce(e.pagerank_score, 0) DESC
                LIMIT 20
            """)
            
        elif any(word in question_lower for word in ['who', 'person', 'people', 'founder', 'ceo']):
            print("\n👤 People found in the document:\n")
            result = session.run("""
                MATCH (e:Entity:PERSON)
                RETURN e.canonical_name as name, e.pagerank_score as score
                ORDER BY coalesce(e.pagerank_score, 0) DESC
                LIMIT 20
            """)
            
        elif any(word in question_lower for word in ['where', 'location', 'place', 'city', 'country']):
            print("\n📍 Locations found in the document:\n")
            result = session.run("""
                MATCH (e:Entity:GPE)
                RETURN e.canonical_name as name, e.pagerank_score as score
                ORDER BY coalesce(e.pagerank_score, 0) DESC
                LIMIT 20
            """)
            
        elif 'founded' in question_lower or 'created' in question_lower:
            print("\n🔗 Founding relationships:\n")
            result = session.run("""
                MATCH (founder)-[r:CREATED]->(org)
                RETURN founder.canonical_name as founder, org.canonical_name as organization
            """)
            
        elif 'located' in question_lower or 'based' in question_lower:
            print("\n📍 Location relationships:\n")
            result = session.run("""
                MATCH (org)-[r:LOCATED_IN]->(loc)
                RETURN org.canonical_name as organization, loc.canonical_name as location
            """)
            
        else:
            # General search
            terms = [word for word in question.split() if len(word) > 3 and word.lower() not in ['what', 'where', 'when', 'which', 'about', 'mentioned']]
            print(f"\n🔍 Searching for: {terms}\n")
            
            results = []
            for term in terms:
                r = session.run("""
                    MATCH (e:Entity)
                    WHERE toLower(e.canonical_name) CONTAINS toLower($term)
                    RETURN e.canonical_name as name, e.entity_type as type, e.pagerank_score as score
                    ORDER BY coalesce(e.pagerank_score, 0) DESC
                    LIMIT 10
                """, term=term)
                results.extend(list(r))
            
            if results:
                seen = set()
                for record in results:
                    if record['name'] not in seen:
                        print(f"• {record['name']} ({record['type']})")
                        seen.add(record['name'])
                return
            else:
                print("No matches found")
                return
        
        # Display results
        results = list(result)
        if results:
            for i, record in enumerate(results, 1):
                if 'founder' in record:
                    print(f"{i}. {record['founder']} founded {record['organization']}")
                elif 'organization' in record and 'location' in record:
                    print(f"{i}. {record['organization']} is located in {record['location']}")
                else:
                    print(f"{i}. {record['name']} (PageRank: {record['score'] or 0:.4f})")
        else:
            print("No results found")
            
            # Show what we do have
            print("\n📊 Available data:")
            counts = session.run("""
                MATCH (e:Entity)
                RETURN e.entity_type as type, COUNT(e) as count
                ORDER BY count DESC
            """)
            for record in counts:
                print(f"  • {record['type']}: {record['count']}")
    
    driver.close()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        question = ' '.join(sys.argv[1:])
        answer_question(question)
    else:
        print("\nUsage: python answer_questions.py 'your question here'")
        print("\nExample questions:")
        print("  • What organizations are mentioned?")
        print("  • Who are the people in the document?")
        print("  • Where are the locations?")
        print("  • What companies were founded?")
        print("  • Where are organizations located?")