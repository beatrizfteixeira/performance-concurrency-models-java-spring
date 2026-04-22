import http from 'k6/http';
import { check } from 'k6';
import { Counter, Trend } from 'k6/metrics';

const successCounter = new Counter('successful_requests');
const failedCounter = new Counter('failed_requests');
const responseTrend = new Trend('response_time_ms');

const vuTarget = parseInt(__ENV.VU_TARGET || '50', 10);
const steadyDuration = __ENV.STEADY_DURATION || '3m';
const appUrl = __ENV.APP_URL || 'http://localhost:8080';

export const options = {
    stages: [
        { duration: '30s', target: vuTarget },
        { duration: steadyDuration, target: vuTarget },
        { duration: '30s', target: 0 },
    ],
    thresholds: {
        http_req_duration: ['p(95)<5000', 'p(99)<10000'],
        http_req_failed: ['rate<0.05'],
        checks: ['rate>0.95'],
    },
    summaryTrendStats: ['min', 'avg', 'med', 'max', 'p(90)', 'p(95)', 'p(99)'],
};

export default function () {
    const endpoint = `${appUrl}/api/io`;

    const res = http.get(endpoint, {
        tags: {
            workload: 'io',
            endpoint: '/api/io',
        },
    });

    const ok = check(res, {
        'status is 200': (r) => r.status === 200,
        'content-type is json': (r) =>
            (r.headers['Content-Type'] || '').includes('application/json'),
        'workloadType is IO-BOUND': (r) => {
            try {
                return JSON.parse(r.body).workloadType === 'IO-BOUND';
            } catch (_) {
                return false;
            }
        },
        'executionTimeMs exists': (r) => {
            try {
                const body = JSON.parse(r.body);
                return typeof body.executionTimeMs === 'number';
            } catch (_) {
                return false;
            }
        },
    });

    responseTrend.add(res.timings.duration);

    if (ok) {
        successCounter.add(1);
    } else {
        failedCounter.add(1);
    }
}