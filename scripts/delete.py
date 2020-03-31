import os, sys, tqdm, shutil
for dir in tqdm.tqdm(os.listdir(sys.argv[1])):
	shutil.rmtree(os.path.join(sys.argv[1], dir))
