import http from 'k6/http';
import { check } from 'k6';
import { Counter, Trend } from 'k6/metrics';

const successCounter = new Counter('successful_requests');
const failedCounter = new Counter('failed_requests');
const responseTrend = new Trend('response_time_ms');
const serverExecTimeTrend = new Trend('server_execution_time_ms');

const totalIterations = parseInt(__ENV.TOTAL_ITERATIONS || '500', 10);
const vuTarget = parseInt(__ENV.VU_TARGET || '10', 10);
const warmupDuration = __ENV.WARMUP_DURATION || '5s';
const appUrl = __ENV.APP_URL || 'http://localhost:8080';

export const options = {
    scenarios: {
        warmup: {
            executor: 'constant-vus',
            vus: vuTarget,
            duration: warmupDuration,
            exec: 'warmupRequest',
            tags: { phase: 'warmup' },
        },
        steady: {
            executor: 'shared-iterations',
            vus: vuTarget,
            iterations: totalIterations,
            maxDuration: '30m',
            startTime: warmupDuration,
            exec: 'steadyRequest',
            tags: { phase: 'steady' },
        },
    },
    thresholds: {
        'http_req_duration{phase:steady}': ['p(95)<5000', 'p(99)<10000'],
        'http_req_failed{phase:steady}': ['rate<0.05'],
        'checks{phase:steady}': ['rate>0.95'],
    },
    summaryTrendStats: ['min', 'avg', 'med', 'max', 'p(90)', 'p(95)', 'p(99)'],
};

function performRequest(phase) {
    const endpoint = `${appUrl}/api/cpu`;

    const res = http.get(endpoint, {
        tags: {
            workload: 'cpu',
            endpoint: '/api/cpu',
            phase: phase,
        },
    });

    let serverExecTime = null;
    const ok = check(res, {
        'status is 200': (r) => r.status === 200,
        'content-type is json': (r) =>
            (r.headers['Content-Type'] || '').includes('application/json'),
        'workloadType is CPU-BOUND': (r) => {
            try {
                return JSON.parse(r.body).workloadType === 'CPU-BOUND';
            } catch (_) {
                return false;
            }
        },
        'executionTimeMs exists': (r) => {
            try {
                const body = JSON.parse(r.body);
                if (typeof body.executionTimeMs === 'number') {
                    serverExecTime = body.executionTimeMs;
                    return true;
                }
                return false;
            } catch (_) {
                return false;
            }
        },
    }, { phase: phase });

    if (phase === 'steady') {
        responseTrend.add(res.timings.duration);
        if (serverExecTime !== null) {
            serverExecTimeTrend.add(serverExecTime);
        }

        if (ok) {
            successCounter.add(1);
        } else {
            failedCounter.add(1);
        }
    }
}

export function warmupRequest() {
    performRequest('warmup');
}

export function steadyRequest() {
    performRequest('steady');
}
