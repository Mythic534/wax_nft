// Loads key from .env file -- Pushes transactions from actions.json file -- Returns txid

import { Api, JsonRpc } from 'eosjs';
import { JsSignatureProvider } from 'eosjs/dist/eosjs-jssig.js';
import { TextEncoder, TextDecoder } from 'util';
import fetch from 'node-fetch';
import fs from "fs";
import { dirname } from "path";
import { fileURLToPath } from "url";
import 'dotenv/config';

const privateKey = process.env.PRIVATE_KEY;
if (!privateKey) {
    console.error("Error: PRIVATE_KEY is not defined in the .env file");
    process.exit(1);
}

const signatureProvider = new JsSignatureProvider([privateKey]);
const rpc = new JsonRpc('https://wax.greymass.com', { fetch });

const api = new Api({
    rpc,
    signatureProvider,
    textDecoder: new TextDecoder(),
    textEncoder: new TextEncoder(),
});

// Dynamically resolve the directory of transfer.js
const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);


async function transferTokens() {
    try {
        const actionsJsonPath = `${__dirname}/actions.json`;

        if (!fs.existsSync(actionsJsonPath)) {
            throw new Error("actions.json file not found");
        }
 
        const actionsData = fs.readFileSync(actionsJsonPath, "utf-8");
        const actions = JSON.parse(actionsData);

        const result = await api.transact(
            { actions: actions },
            {
                blocksBehind: 3,
                expireSeconds: 30,
            }
        );
        
        console.log(result.transaction_id);

    } catch (error) {
        console.error(JSON.stringify(error.json || { message: error.message }));
        process.exit(1);
    }
}

transferTokens();