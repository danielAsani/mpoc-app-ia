import logging
import time

from . import config, llm, rag
from .safety import check_question

logger = logging.getLogger('mpoc.metrics')


def answer_question(question, baseline=False):
    started = time.perf_counter()
    result = dict(answer='', sources=[], status='answered', disclaimer=config.DISCLAIMER)
    metrics = dict(passages_found=0, sources_used=0, input_tokens=0, output_tokens=0, estimated_cost_usd=None)
    refusal = check_question(question)
    if refusal:
        result['status'], result['answer'] = refusal
    else:
        retrieval_started = time.perf_counter()
        passages = [] if baseline else rag.search(question)
        metrics['retrieval_ms'] = round((time.perf_counter() - retrieval_started) * 1000)
        metrics['passages_found'] = len(passages)
        if not passages and not baseline:
            result.update(status='insufficient', answer=config.INSUFFICIENT)
        else:
            generation_started = time.perf_counter()
            generated, usage = llm.generate(question, passages, baseline)
            metrics['generation_ms'] = round((time.perf_counter() - generation_started) * 1000)
            metrics.update(usage)
            ids = generated['source_ids']
            allowed = {p['id']: p for p in passages}
            valid = all(type(i) is int and i in allowed for i in ids)
            if not baseline and (generated.get('sufficient') is not True or not ids or not valid or not generated['answer'].strip()):
                result.update(status='insufficient', answer=config.INSUFFICIENT)
            else:
                result['answer'] = generated['answer']
                result['sources'] = [allowed[i] for i in dict.fromkeys(ids)] if not baseline else []
    metrics.update(sources_used=len(result['sources']), elapsed_ms=round((time.perf_counter() - started) * 1000))
    result['metrics'] = metrics
    # Ni question, ni réponse, ni données personnelles dans les journaux.
    logger.info('status=%s metrics=%s', result['status'], metrics)
    return result
