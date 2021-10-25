myproj JSON-based Configuration Server & Client Overview

* Please see more details and diagrams in myproj wiki
  * https://gitlab.openkbs.org/myproj/myproj/-/wikis/myproj-APP-Container-Platforms/%233:-myproj-JSON-Configuration-Server-&-Client-Overview
* JSON-based (Central) Configuration Server Design and Automation Workflow:
  * JSON-based Configuration Server:
    * use the YAML file as the specifications for defining Configuration for all myproj services that each myproj services will use HTTP REST Clients (Python, Java, NodeJS, Shell (curl)) to access the specific Configuration Object using ConfigObjectUID (e.g., as the URL routing appended behind the URL address (e.g., http://abdn-vm-155.openkbs.org:3000/) and the full URL to access (download) specific ConfigObjectUID (e.g., myproj_config_LOCAL_abdn-vm-166.openkbs.org ) will be like:
      * http://abdn-vm-155.openkbs.org:3000/myproj_config_LOCAL_abdn-vm-166.openkbs.org
* JSON-based (Central) Configuration Java Client Design and Automation Workflow
  * Wiki: https://gitlab.openkbs.org/myproj/myproj/-/wikis/Developer-Guide/myproj-JSON-based-Configuration-Server-Automation-Workflow
  * The Java Client design used two Architecture Design Patterns:
    * Singleton Design Pattern
    * Façade Design Pattern
  * JSON-based Java Client Library can be extended to cover distributed distributed storeage such as
    * Memcache
    * Redis
    * RDBMS
    * NoSQL (Mongo, etc)
    * RDF/OWL Datastores (Allegograph (commercial), Blazegraph (open source), Sparkdog (commercial), GraphDB (commercial), Apache Seasme
    * Neo4J (Graph DB)
    * And, any tools/datastores.
