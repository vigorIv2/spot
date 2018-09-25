package com.huhula;

import org.web3j.crypto.Credentials;
import org.web3j.crypto.ECKeyPair;
import org.web3j.utils.Numeric;

import java.math.BigInteger;

public class SampleKeys {

// vqlid set
//    public static final String PRIVATE_KEY_STRING =
//            "a392604efc2fad9c0b3da43b5f698a2e3f270f170d859912be0d54742275c5f6";
//    static final String PUBLIC_KEY_STRING =
//            "0x506bc1dc099358e5137292f4efdd57e400f29ba5132aa5d12b18dac1c1f6aab"
//                    + "a645c0b7b58158babbfa6c6cd5a48aa7340a8749176b120e8516216787a13dc76";

//    Address:0xcdea3bfc82cbe46b8a7a8a648eda0969f145468a
//    Public Key:0xebed9b26ac5fb2635454323ea2888f4cff1b3f9d8f7d99c1227495a2a4b54754e582be09bdd838ccd45144c44649049ac44902b2d6589874ef0d2a117d0
//    Private Key:0xbaa95866bfe082dccef8ec1a741c2ceeed0f3f4c1cf162428724c8bb927067ca

    public static final String PRIVATE_KEY_STRING =
            "5641128d7d895f185d91fa2b83dffe646eede097d1a85c3247debc2b75219d92";
    static final String PUBLIC_KEY_STRING =
            "0xdcaa05bb5a82e0d1675d7f9b12b4d1948122500fc35ca7dee2edc99f2a3af2c5d6498f80dfbc0ab7c624793919aee8e4651adeefa7951c96438cad7838fbb9ea";
    public static final String ADDRESS = "0x7c06350cb8640a113a618004a828d3411a4f32d3";
    public static final String ADDRESS_NO_PREFIX = Numeric.cleanHexPrefix(ADDRESS);

//    public static final String PASSWORD = "copy obey episode awake damp vacant protect hold wish primary travel shy";
    public static final String PASSWORD = "copy obey episode awake damp vacant protect hold wish primary travel shy";

    static final BigInteger PRIVATE_KEY = Numeric.toBigInt(PRIVATE_KEY_STRING);
    static final BigInteger PUBLIC_KEY = Numeric.toBigInt(PUBLIC_KEY_STRING);

    static final ECKeyPair KEY_PAIR = new ECKeyPair(PRIVATE_KEY, PUBLIC_KEY);

    public static final Credentials CREDENTIALS = Credentials.create(KEY_PAIR);

    public static final BigInteger gasPrice = Numeric.toBigInt("20000000000");
//    public static final BigInteger gasPrice = Numeric.toBigInt("100000000");

    public static final BigInteger gasLimit = Numeric.toBigInt("7984452");
//    public static final BigInteger gasLimit =        Numeric.toBigInt("4921919");

    private SampleKeys() {}
}
