// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.0;

contract CustomerBalance {
    mapping(address => mapping(bytes32 => uint)) balances;

    event BalanceUpdate(address indexed customer, bytes32 indexed currency, uint amount);

    function deposit(bytes32 currency, uint amount) public {
        balances[msg.sender][currency] += amount;
        emit BalanceUpdate(msg.sender, currency, balances[msg.sender][currency]);
    }

    function withdraw(bytes32 currency, uint amount) public {
        require(balances[msg.sender][currency] >= amount, "Insufficient balance");
        balances[msg.sender][currency] -= amount;
        emit BalanceUpdate(msg.sender, currency, balances[msg.sender][currency]);
    }

    function getBalance(address customer, bytes32 currency) public view returns (uint) {
        return balances[customer][currency];
    }
}