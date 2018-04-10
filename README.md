# discrete-bayes-machine-learning-algorithm
Quantizes real data and applies discrete bayes rule to achieve highest expected value.

Uses bruteforce hill climbing to find optimal boundaries for quantization.

Uses K smoothing to smooth probabilities of low probability intervals.

See write up for results.

#Setup:
pip install -r requirements.txt

download observations.db from https://drive.google.com/open?id=1x-JfYVIih0mbSA1_D1Li1ZTf486l0zdT
and place it in the root of this project.

#Run Tests:
python -m tests.test_discrete_bayes
python -m tests.test_quantizer

#Run Optimizations:
to find optimal boundaries:
python -m unittest tests.test_optimizer.TestOptimizer.test_optimize_bounds

to evaluate bounds:
python -m unittest tests.test_optimizer.TestOptimizer.test_eval_bounds

