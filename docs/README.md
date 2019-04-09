# Nautilus

Today Nautilus is a close approximation of the infrastructure that [Cryptonomic](https://cryptonomic.tech) runs internally. A full deployment includes a Tezos node, a [Conseil](https://github.com/Cryptonomic/Conseil) node, a Postgres DB and a server hosting the [Arronax](https://github.com/Cryptonomic/Arronax) block explorer. We encourage customization that suits your needs. These services enable us to run [Tezori/Galleon](https://galleon-wallet.tech), a wallet for Tezos.

## Actually Decentralized

## Quick-start

## Scaling

We consider a Nautilus deployment as a unit, meaning we do not currently run odd collections of these services. This approach may not be suited to all use-cases however.

The most obvious scaling optimization is to run a single Tezos node, with a single Conseil writer service (Lorre), a single Postgres DB, and multiple Conseil reader nodes configured as a dns-round-robin cluster as back-end for something like Arronax.

## Operating requirements

Below is a selection of recommendations targeting various deployments. These are incomplete suggestions as they take no opinion on *your* security requirements. We do not operate any of these configurations as described in production. We have tested extensively in sandboxed environments.

### Bare Metal

### Cloud-hosted

Under most circumstances a small VM instance would be enough to run any of these components. We have seen reasonable performance with "small" 2-core instances with 4GB of RAM. Budget-permitting, especially if the spec calls for snappier performance, more RAM helps. Under some conditions, like a bare initialization where both the Tezos node and Conseil (Lorre) need to catch up to the current head starting with the genesis block, more cores will also help.

### Docker-centric

Docker adds some overhead. The most cost-effective configuration with cloud-hosted Dockerized environments that we found was to run the Tezos container independently and then run Postgres and Conseil images on a single 4-core VM in Docker.
