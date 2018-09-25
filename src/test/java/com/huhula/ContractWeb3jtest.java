package com.huhula;

import com.huhula.contract.HuhulaSale;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.web3j.crypto.Credentials;
import org.web3j.crypto.WalletUtils;
import org.web3j.protocol.Web3j;
import org.web3j.protocol.core.methods.response.TransactionReceipt;
import org.web3j.protocol.http.HttpService;
import org.web3j.tx.Contract;
import org.web3j.tx.ManagedTransaction;
import org.web3j.tx.Transfer;
import org.web3j.utils.Convert;

import java.math.BigDecimal;

public class ContractWeb3jtest {
    private static final Logger log = LoggerFactory.getLogger(ContractWeb3jtest.class);

    public static void main(String[] args) throws Exception {
        new ContractWeb3jtest().run();
    }

    private void run() throws Exception {
        // We start by creating a new web3j instance to connect to remote nodes on the network.
        Web3j web3j = Web3j.build(new HttpService());
        log.info("Connected to Ethereum client version: "
                + web3j.web3ClientVersion().send().getWeb3ClientVersion());
        Credentials credentials =
                WalletUtils.loadCredentials(
                        "password",
                        "chaindata\\keystore\\UTC--2018-06-21T06-34-32.658490800Z--5ade9a7f8f57ab3995ac4d56c78a22649d3b1686");
        log.info("Credentials loaded");
        log.info("Sending Ether ..");
        TransactionReceipt transferReceipt = Transfer.sendFunds(
                web3j, credentials,
                "0xDc1Fb60F7E1eF6ef052A014EFbDF82debd803D06",  // you can put any address here
                BigDecimal.valueOf(100), Convert.Unit.ETHER)  // 1 wei = 10^-18 Ether
                .sendAsync().get();
        log.info("Transaction complete : "
                + transferReceipt.getTransactionHash());


        // Now lets deploy a smart contract
        log.info("Deploying smart contract");
        HuhulaSale contract = HuhulaSale.deploy(
                web3j, credentials,
                ManagedTransaction.GAS_PRICE, Contract.GAS_LIMIT).send();

        String contractAddress = contract.getContractAddress();
        log.info("Smart contract deployed to address " + contractAddress);

        log.info("Initial value of counter in Smart contract: " + contract.buyBackRate().send());
        log.info("Incrementing counter in Smart contract");
        contract.owner().send();
        log.info("Value of counter in Smart contract after increment : " + contract.rate().send());
        log.info("Decrementing counter in Smart contract");
        contract.token().send();
        log.info("Final value of counter in Smart contract : " + contract.closingTime().send());
    }
}