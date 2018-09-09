package com.huhula.credentials;

import org.web3j.crypto.WalletUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;

import java.io.File;

public class Wallets {

    private java.io.File tempDir ;
    private static final Logger LOG = LoggerFactory.getLogger(Wallets.class);

    public Wallets(String _tempDir) {
        tempDir = new File(_tempDir);
    }

    public String get_SHA_512_SecurePassword(String passwordToHash, String salt){
        String generatedPassword = null;
        try {
            MessageDigest md = MessageDigest.getInstance("SHA-512");
            md.update(salt.getBytes(StandardCharsets.UTF_8));
            byte[] bytes = md.digest(passwordToHash.getBytes(StandardCharsets.UTF_8));
            StringBuilder sb = new StringBuilder();
            for(int i=0; i< bytes.length ;i++){
                sb.append(Integer.toString((bytes[i] & 0xff) + 0x100, 16).substring(1));
            }
            generatedPassword = sb.toString();
        }
        catch (NoSuchAlgorithmException e){
            e.printStackTrace();
        }
        return generatedPassword;
    }

    public String generateWallet(String password) {
        String content = "";
        String fileName = "";
        try {
            fileName = WalletUtils.generateFullNewWalletFile(password, tempDir);
            content = new String(Files.readAllBytes(Paths.get(fileName)));
        } catch (Throwable t) {
            LOG.error("Error while creating wallet file",t);
        } finally {
            if ( ! fileName.isEmpty() ) {
                try {
                    Files.delete(Paths.get(fileName));
                } catch ( Throwable et ) {
                    LOG.error("Error on attempt to delete file "+fileName);
                }
            }
        }
        return content;
    }

    public static void main(String [] args) {
        Wallets ws = new Wallets("/Users/ivasilchikov/spot");
        String pwd = ws.get_SHA_512_SecurePassword("0414cae0-0492-4e2e-bd58-230938eb06a9","110865176290720544754");
        String keyFileName = ws.generateWallet(pwd);
        System.out.println("Wallet file content "+keyFileName);
        System.out.println("Wallet pwd "+pwd);

    }
}
