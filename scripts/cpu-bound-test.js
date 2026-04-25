import http from 'k6/http';
import { check } from 'k6';
import { Counter, Trend } from 'k6/metrics';

const successCounter = new Counter('successful_requests');
const failedCounter = new Counter('failed_requests');
const responseTrend = new Trend('response_time_ms');
const serverExecTimeTrend = new Trend('server_execution_time_ms');

const totalIterations = parseInt(__ENV.TOTAL_ITERATIONS || '1000', 10);
const vuTarget = parseInt(__ENV.VU_TARGET || '10', 10);
const appUrl = __ENV.APP_URL || 'http://localhost:8080';

export const options = {
    scenarios: {
        fixed_load: {
            executor: 'shared-iterations',
            vus: vuTarget,
            iterations: totalIterations,
            maxDuration: '30m',
        },
    },
    thresholds: {
        http_req_duration: ['p(95)<5000', 'p(99)<10000'],
        http_req_failed: ['rate<0.05'],
        checks: ['rate>0.95'],
    },
    summaryTrendStats: ['min', 'avg', 'med', 'max', 'p(90)', 'p(95)', 'p(99)'],
};

export default function () {
    const endpoint = `${appUrl}/api/cpu`;

    const res = http.get(endpoint, {
        tags: {
            workload: 'cpu',
            endpoint: '/api/cpu',
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
    });

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
