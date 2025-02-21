// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract BankContract{

    string public SECURITY_POLICY = "SECURITY_POLICY global: eIDAS2 DataAct--";
    string public SECURITY_POLICY_HelloWorld = "SECURITY_POLICY HelloWorld(): By executing the function below, the executor agree of legal terms and conditions as defined in LEGAL_CITATION--";
    string public LEGAL_CITATION = "LEGAL_CITATION: Made by www.sagrada-familia-legal.com--";

    function HelloWorld() public pure returns (string memory){
        return "HelloWorld";
    }
}


