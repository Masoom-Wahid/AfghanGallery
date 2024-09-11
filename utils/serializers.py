from typing import Dict, List
from rest_framework.validators import UniqueValidator

def generate_keyword_args(
    *,
    fields : List[str],
    unique_names : List[str],
    model : object
) -> Dict[str,Dict]:
    """
    Generates a extra_kwargs dict for the the given serializer,
    helpful to automate the custom Err Messages
    """
    extra_kwargs = {}
    for field in fields:
        extra_kwargs[field] = {
                    'error_messages' : {
                        'required' : "ERR_REQUIRED",
                        "generic" : "ERR_GENERIC"
                    }, 
            }
        if field in unique_names:
            extra_kwargs[field]["validators"] = [
                        UniqueValidator(
                            queryset=model.objects.all(), #type:ignore
                            message="ERR_EXISTS"
                        )
                             
                    ]
    return extra_kwargs




