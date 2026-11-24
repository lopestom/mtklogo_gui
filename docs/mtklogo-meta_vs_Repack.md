# Analysis of the mtklogo Source Code to Understand the mtklogo-meta File

## Table of Contents

- [Is there any reference to mtklogo-meta in any file?](#is-there-any-reference-to-mtklogo-meta-in-any-file)
- [What is this file for and what is it based on?](#what-is-this-file-for-and-what-is-it-based-on)
- [“Negative issue” and "Solution"](#negative-issue-with-mtklogo-optionprocess)
  - [User choice](#user-choice)
  - [Understanding Warnings](#understanding-warnings)

## Is there any reference to mtklogo-meta in any file?

Yes, but only as a `.mtklogo-meta` sidecar file (not as a binary/command):
- `cli/src/command/meta.rs:5,18,28` — creation/reading of the file
- `cli/src/command/repack.rs:25` — comment about the sidecar
- `README.org:96` — repack documentation
- `mtklogo_v1.1/mtklogos.sh:139` — comment about the `-n` mode of unpack

## What is this file for and what is it based on?

The `.mtklogo-meta` is an auxiliary (sidecar) file of mtklogo itself, not an official MTK/Android format.

**What it is for**

- Created by `unpack` in the output directory (`cli/src/command/unpack.rs:103`).
- Stores what the PNGs do not carry: the 512-byte MTK header (legacy or extended) and the ASN.1 certificate (`cert` + `cert_inner_len`).
- `repack` reads it from the input directory (`cli/src/command/repack.rs:44`) and restores the header/certificate, generating a `logo.bin` compatible with the original device. If it is absent/invalid, it uses a default header and no certificate.

**What it is based on**

- Its own versioned layout: `[MTKL][cert_inner_len: u32 LE][header 512 B][cert]` (`cli/src/command/meta.rs:6-16`).
- It is based on the `logo.bin` structures: `MtkHeader` (`src/mtk/header.rs`, `SIZE = 512`) and `LogoImage.cert`/`cert_inner_len` (`src/mtk/logo.rs:24-27`, where `cert_inner_len = dsize - block_size`).
- It already existed in v1.0.1; the v1.1.0 patch did not create it.

## “Negative issue” with mtklogo option/process -- A human user performed all the tests and found the solution!

When the user chooses “Repack”, the `.mtklogo-meta` file is placed/inserted together with the PNG images/figures, going straight into the modified `logo_Mod.bin`. This causes a file-size error relative to the original/stock `logo.bin`.

The solution was to delete the `.mtklogo-meta` file and perform the “Repack” choice again. In that sense, the size was smaller than the original `logo.bin` file.

Example: the original `logo.bin` file is 8.0 MB (8,388,608 bytes).  
The `logo_.bin` file created (“Repack”) from the presence of `.mtklogo-meta`, that is, without deleting the `.mtklogo-meta` file, had a size of 10.7 MB (11,210,656 bytes).

Another test was done: only running `Unpack` on the original `logo.bin` file, which is 8.0 MB (8,388,608 bytes), and without changing any image/figure, choosing “Repack”, the `logo_.bin` file had the same size of 8.0 MB (8,388,608 bytes). When removing the `.mtklogo-meta` file, the `logo_.bin` file had a size of 6.0 MB (6,265,740 bytes).

Most of the tests happened on `logo.bin` files from devices that:
- Had some company signature or lock;
- Were devices with an “old” architecture.

On devices with a maximum `/logo` partition size of 8,388,608 bytes, there is the resolution 1080x2340x4 with 10,108,800 bytes. In the case of the original PNG images, performing `Repack` without the `.mtklogo-meta` file gives 3,443,696 bytes. Since the `.mtklogo-meta` file has an “exaggerated” size, including it with modified images larger than what can be allowed makes the `Repack` of the file also exaggerated.

In all these specific cases, the `.mtklogo-meta` file may have a size of 4.7MB or larger, or a size that limits the installation of the modified `logo.bin`, which “gets in the way”. Even though it is a hidden file, the logic was to have something safe in such cases. What cannot be done now is remove or manipulate it, since it is for the user's/device's own safety.

In summary, the `.mtklogo-meta` file should be moved to the `/mtklogo-gui/backup` folder, thus resolving the “Repack” process and ensuring the user can safely install the `logo_.bin` file.

### User choice

If any user wants to restore the `.mtklogo-meta` file, that is, without deleting the `.mtklogo-meta` file during “Repack”, and test it, there is an alternative. But I warn in advance to observe the size of the `.mtklogo-meta` file before any changes/modifications. Everything will depend on the exact size of the `logo_` partition and the size of the generated `.mtklogo-meta` file. If a stock `logo.bin` has 8MB total to be installed in the partition, run “Unpack”, check in the `/logo` folder whether the modified PNG images + the `.mtklogo-meta` file will not exceed that total size.

In many cases, the size of the `.mtklogo-meta` file may be only 4.2KB, and that is ideal for tests on devices that have signature barriers. In all cases, for any action/manipulation/modification made by the user, the responsibility is entirely the user's own!

For tests with the `.mtklogo-meta` file, open the `mtklogos.sh` file in the `/mtklogo-gui` folder; find and delete the lines containing `_meta_to_backup`.  
Delete the `.mtklogo-meta` file in the `/backup` folder and run “Unpack” to ensure the process, with the modified PNG images, choose “Repack”, and check that the `.mtklogo-meta` file was not moved.

If you want to revert to how it was before, close the application, delete the `/mtklogo-gui/mtklogos.sh` file, and open the application again.

### Understanding Warnings

In the tests performed, `logo_Mod.bin` exceeded the original (stock) file submitted at 7.7 MB (8060256 bytes), and mtklogo_v1.4 repacked it at 9.3 MB (9716432 bytes).

Everything is shown in the mtklogo_v1.4 prompt:
```bash
size: 987904 bytes (original 159808 bytes, +828096 bytes)
warning: the new image is more than 5% bigger than the original; check that it fits in your logo partition.
```
However, it is important to know the size of the `/logo` partition in advance to avoid surprises!

On MediaTek devices, the values can be found with `fastboot getvar all` or with the `MTnnnn_Android_scatter.xml` file. As an example, this XML file is from the Unihertz TANK5 and has:

```ruby
partition - name => hexadecimal = decimal (size bytes) ~ size MB
logo_a - logo.img => 0xe00000 = 14680064 ~ 14.68MB
logo_b - NONE => 0x900000 = 9437184 ~ 9.73MB
```

Therefore, in this Unihertz TANK5 case, it is possible to install the `logo_Mod.bin` file without problems.

If the `logo_Mod.bin` file were larger than 14.68MB, using `fastboot` gives `FAIL`, but when using SPFT some partition will receive some bytes as an overlap and thus leave the device in softbrick mode.

> [!CAUTION]
> Again, this is a WARNING message to reflect on your decision, since you have read everything up to this point.
> Good Luck!
