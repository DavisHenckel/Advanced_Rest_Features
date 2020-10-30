#Required Functionality
#Operations on Boats
* Create a boat
  Request must be JSON.
  Response must be JSON.
* Delete a boat
* Edit a boat
  Request must be JSON.
  Response must be JSON.
  Updating the value of id is not allowed.
  Your application must support both PATCH and PUT.
* PATCH
  Allows updating any subset of attributes while the other attributes remain unchanged.
  E.g., update only the name, or update only name and length.
* PUT
  All attributes are modified (except, of course, id).
  This must return status code 303 as discussed later.
* View a boat
  Your application must support viewing an individual boat either as JSON or HTML depending on the Accept header sent by the client. The options being application/json or text/html.
The HTML view of the boat doesn't have to be fancy. Just returning the boat as a simple ul with the attributes as li would be sufficient.
Constraint Maintenance
Your application needs to ensure that the name of a boat is unique across all boats.
This constraint must be maintained when a boat is created as well as when an existing boat is updated.
Note: For maintaining this constraint, you do not need to worry about race conditions. In other words, you don't need to account for cases where two or more requests simultaneously try to create and/or update boats with the same name.
Request Validation
Your application cannot assume that the data in the request is valid, so you must validate the input.
You must
Think about possible invalid input values.
Impose reasonable restrictions to define what your application considers to be valid input.
Document the restrictions and the behavior of your application when dealing with such invalid input.
Implement your code so that it properly handles invalid input, and returns the appropriate status code and message per your API documentation.
Here are some examples of input validation you should think about
What characters should be allowed in the name attribute?
Can the name attribute be arbitrarily long?
If a request has extraneous attributes (e.g., color), what is the behavior of the application?
The above examples of input validation are just a sample and are not meant to be exhaustive.
You should think about additional input validation that should be performed by your application.
The goal is that your application should be robust enough such that invalid input data doesn't cause it to throw an error and return an inappropriate status code and/or message.
Content Types
Your API doc must specify the MIME type (or types) in which an endpoint is willing to accept data from requests .
Your API doc must specify the MIME type of all responses sent by the endpoints.
Your implementation must conform to the specification of MIME types in your API doc.
Status Codes
All responses must have the appropriate status codes
You should appropriately use the following 2xx status codes
200
201
204
You should appropriately use the following 3xx status codes
303
When PUT is used to edit a boat, the response should return a 303 code with the location of the updated boat in the appropriate header field
You should appropriately use the following 4xx status codes
400
Use this for requests with invalid data
E.g., missing attributes, invalid value of attribute
403
Use this for violations of the uniqueness constraint
404
405
Use this for PUT or DELETE requests on the root boat URL
Because you are not supporting  edit or delete of the entire list of boats!
406
Use this when the client requests a content type not supported by the endpoint
415
Use this when the client sends an unsupported media type to the endpoint
