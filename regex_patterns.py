# Datatype Patterns
REGEX_INT = "^[0-9]+$"  # Allows for any positive integer
REGEX_STR_NO_SPECIAL_CHARS = "^[a-zA-Z0-9_ ]+$"  # Allows for any string with no special characters

# Boolean Patterns
REGEX_BOOL = "^(true|false|yes|no|t|f|y|n)$"  # Allows for any boolean value
REGEX_BOOL_TRUE = "^(true|yes|t|y)$"  # Allows for any true boolean value
REGEX_BOOL_FALSE = "^(false|no|f|n)$"  # Allows for any false boolean value
REGEX_BOOL_YES = "^(yes|y)$"  # Allows for any yes boolean value
REGEX_BOOL_NO = "^(no|n)$"  # Allows for any no boolean value

# AWS Patterns
REGEX_AWS_S3_BUCKET_NAME = "(?!(^xn--|.+-s3alias$))^[a-z0-9][a-z0-9-]{1,61}[a-z0-9]$"
REGEX_AWS_ACCOUNT_ID = "^[0-9]{12}$"
