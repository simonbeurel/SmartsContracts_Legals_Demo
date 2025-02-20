import json

TEMPLATE = """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract LegalTextsRegistry {{

    {variables}

}}
"""

with open("legal_terms.json", "r") as file:
    terms = json.load(file)

variables = "\n    ".join([f'string public {key}_{i} = "{text}";' for key, values in terms.items() for i, text in enumerate(values)])

contract_code = TEMPLATE.format(
    variables=variables,
    SECURITY_POLICY=" | ".join(terms.get("SECURITY_POLICY", [])),
    LEGAL_TERMS=" | ".join(terms.get("LEGAL_TERMS", []))
)

with open("LegalTextsRegistry.sol", "w") as file:
    file.write(contract_code)

print("✅ Smart Contract template generated successfully !")
