# Fix for TypeError: _compute_lst() got unexpected keyword argument

## Problem
Your code tries to use the newer `using_lst_runner.py` tutorial, but your installed `pylst` package is loading old code from the `build/` cache directory.

The old code has a different API:
- **Old (in build/)**: Split-window algorithms used `split_window/` as a package directory with different method signatures
- **New (in source/)**: Split-window algorithms use `split_window.py` module with correct signatures

When Python imports `pylst`, it may load the stale code from `build/`, causing the TypeError.

## Solution: Complete Reinstall

### Step 1: Close Jupyter/Python
Close your Jupyter notebook and any Python kernels.

### Step 2: Delete Build Cache
Open PowerShell and run:
```powershell
cd d:\pylst0.0.3
Remove-Item -Recurse -Force build -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force pylst.egg-info -ErrorAction SilentlyContinue  
Remove-Item -Recurse -Force dist -ErrorAction SilentlyContinue
```

### Step 3: Clean Python Cache
```powershell
# Remove all __pycache__ directories
Get-ChildItem -Path "." -Filter "__pycache__" -Recurse -Directory | ForEach-Object { Remove-Item -Recurse -Force $_ }
```

### Step 4: Reinstall Package
```powershell
pip install -e . --no-cache-dir --force-reinstall
```

### Step 5: Verify Installation  
```powershell
python verify_install.py
```

You should see:
```
✓ kerr                  PASSED (mean LST: XXX.X K)
✓ sobrino-1993          PASSED (mean LST: XXX.X K)
✓ mcmillin              PASSED (mean LST: XXX.X K)
✓ ALL TESTS PASSED - Package is correctly installed!
```

### Step 6: Restart Jupyter
In Jupyter, restart the kernel: `Kernel → Restart Kernel`

Then run your `using_lst_runner.py` code again - it should now work!

## Why This Happens
Editable installs (`pip install -e .`) can cache old compiled code (.pyc files) and reference old build directories if they exist. Clearing the build directory forces Python to rebuild from current source.

## Need Help?
If you still see errors after these steps:
1. Verify that `d:\pylst0.0.3\build` directory no longer exists
2. Check that your Jupyter kernel was restarted (not just your notebook cell)
3. Run `verify_install.py` to pinpoint which algorithm is failing
