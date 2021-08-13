<img align="right" src="https://serux.pro/9e83af1581.png" height="150" width="150">

# Lavalink.py
**This is a modified version for the godbot**

Lavalink.py is a wrapper for [Lavalink](https://github.com/freyacodes/Lavalink) which abstracts away most of the code necessary to use Lavalink, allowing for easier integration into your projects, while still promising full API coverage and powerful tools to get the most out of it.

## Features
- Regions
- Multi-Node Support
- Load Balancing (this includes region-based load balancing)
- Equalizer

## Optional Dependencies
*These are used by aiohttp.*

## Supported Platforms
While Lavalink.py supports any platform Python will run on, the same can not be said for the Lavalink server.
The Lavalink server requires an x86-64 (64-bit) machine running either Windows, or any Linux-based distro.
It is highly recommended that you invest in a dedicated server or a [VPS](https://en.wikipedia.org/wiki/Virtual_private_server). "Hosts" like Glitch, Heroku, etc... are not guaranteed to work with Lavalink, therefore you should try to avoid them. Support will not be offered should you choose to try and host Lavalink on these platforms.

### Exceptions
The exception to the "unsupported platforms" rule are ARM-based machines, for example; a Raspberry Pi. While official Lavalink builds do not support the ARM architecture, there are [custom builds by Cog-Creators](https://github.com/Cog-Creators/Lavalink-Jars/releases) that offer ARM support. These are the official builds, with additional native libraries for running on otherwise unsupported platforms.
