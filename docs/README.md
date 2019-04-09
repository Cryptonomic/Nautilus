# Nautilus

Today Nautilus is a close approximation of the infrastructure that [Cryptonomic](https://cryptonomic.tech) runs internally. A full deployment includes a Tezos node, a [Conseil](https://github.com/Cryptonomic/Conseil) node, a Postgres DB and a server hosting the [Arronax](https://github.com/Cryptonomic/Arronax) block explorer. We encourage customization that suits your needs. These services enable us to run [Tezori/Galleon](https://galleon-wallet.tech), a wallet for Tezos.

## Actually Decentralized

## Quick-start

## Scaling

We consider a Nautilus deployment as a unit, meaning we do not currently run odd collections of these services. This approach may not be suited to all use-cases however.

The most obvious scaling optimization is to run a single Tezos node, with a single Conseil writer service (Lorre), a single Postgres DB, and multiple Conseil reader nodes configured as a dns-round-robin cluster as back-end for something like Arronax.

## Operating requirements

### Bare Metal

### Cloud-hosted

### Docker-centric
