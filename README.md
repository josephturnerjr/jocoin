# JoCoin

JoCoin is an attempt to implement the more interesting parts of Bitcoin
that I've come across in my readings. It's a grey-box reimplementation,
having only read high-level descriptions of what it is and how it works.
For fun bonus points, I also implemented RSA key generation and signatures
from scratch.

## How to play with JoCoin

  1. Checkout the code.
  2. Generate yourself a key:

            python client.py genkeys > my.key
  3. Start a node locally:

            python node.py -k my.key
     This will start mining with your key. Give it a few minutes (or
     change the difficulty level in `jocoin/chain.py`) to create some
     JoCoins.
  4. Generate another key, say, myother.key
  5. Start another node, using the first node as the seed

            python node.py -k myother.key localhost 9999
  5. Interact with your node using the client

     a. Check your balance:

            python client.py balance my.key
     b. Transfer some JoCoins

            python client.py transfer my.key myother.key 1.23

Run the `client.py` script with the `-h` argument for more information on
possible actions the client can take.

## Things that aren't so great

See the TODO file for things left undone. Most notably, this makes no
effort to be efficient, as i was primarily interested in learning about
how BTC protects the integrity of the blockchain. I also kind of punted
a little bit on making the networking and threading aspects bulletproof
because, again, that wasn't the part I was interested in. 
