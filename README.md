A simple script I might expand upon that lets me save all files under a
download page on vector.co.jp.

example usage for now:

python3 backup.py 'https://www.vector.co.jp/soft/dos/hardware/se000298.html'

will make a directory in your current path called 'se000298' and save two files
under it, `cdsdstd2.lzh` and `std8a.lzh`.

It currently does not save metadata and stuff. It probably should.
