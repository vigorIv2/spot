package com.huhula;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.web3j.crypto.Credentials;
import org.web3j.crypto.WalletUtils;
import org.web3j.protocol.Web3j;
import org.web3j.protocol.core.methods.response.TransactionReceipt;
import org.web3j.protocol.http.HttpService;
import org.web3j.tx.Transfer;
import org.web3j.utils.Convert;
import java.math.BigDecimal;

public class Web3jtest {

    private static final Logger log = LoggerFactory.getLogger(Web3jtest.class);

    public static void main(String[] args) throws Exception {
        new Web3jtest().run();
    }

    private void run() throws Exception {
        // We start by creating a new web3j instance to connect to remote nodes on the network.
        String testrpc_url = "http://localhost:7546";
        Web3j web3j = Web3j.build(new HttpService(testrpc_url));
        log.info("Connected to Ethereum client version: "
                + web3j.web3ClientVersion().send().getWeb3ClientVersion());
        Credentials credentials =
                WalletUtils.loadCredentials(
                        "2945765d553d53e4696ad1b86ea8e30b3544e18d",
                        ".utc-acct.json");

        log.info("Credentials loaded");
        log.info("Sending Ether ..");

        TransactionReceipt transferReceipt = Transfer.sendFunds(
                web3j, credentials,
                credentials.getAddress(),  // you can put any address here
                BigDecimal.valueOf(100), Convert.Unit.ETHER)  // 1 wei = 10^-18 Ether
                .sendAsync().get();
        log.info("Transaction complete : "
                + transferReceipt.getTransactionHash());
    }
}
