Paper Recreations
=================
This library is a collection of tools for PDDL model generation extracted from natural language driven by large language models. This library is an expansion from the survey paper **Leveraging Large Language Models for Automated Planning and Model Construction: A Survey**. Papers that have been reconstructed so far and can be found in the GitHub repo. This list will be updated in the future.

Below is L2P code reconstruction of "action-by-action algorithm" from `"Leveraging Pre-trained Large Language Models to Construct and Utilize World Models for Model-based Task Planning" <https://arxiv.org/abs/2305.14909>`_:

.. code-block:: python
    :linenos:

    max_iterations = 2
    predicate_list = []
    for i_iter in range(max_iterations):
        prev_predicate_list = deepcopy(predicate_list)
        
        action_list = []

        for i_action, action in enumerate(actions):

            if len(predicate_list) == 0:
                # if no predicates in list
                action_prompt = action_prompt.replace('{predicates}', '\nNo predicate has been defined yet')
            else:
                readable_results = ""
                for i, p in enumerate(predicate_list):
                    readable_results += f'\n{i + 1}. {p["raw"]}'
                    
                action_prompt = action_prompt.replace('{predicates}', readable_results)

            pddl_action, new_predicates, llm_response = domain_builder.extract_pddl_action(
            model=model, 
            domain_desc=domain_desc,
            prompt_template=action_predicate_prompt, 
            action_name=action,
            action_desc=action_model[action]['desc'],
            predicates=predicate_list,
            types=hierarchy_requirements["hierarchy"]
            )

            new_predicates = parse_new_predicates(llm_response)
            predicate_list.extend(new_predicates)
            
            action_list.append(pddl_action)
            predicate_list = prune_predicates(predicate_list, action_list)

    return predicate_list, action_list

Current Model Construction Works
--------------------------------
This section provides a taxonomy of research within Model Construction. For more detailed overview, visit our `paper <https://puginarug.com>`_.

Task Translation Frameworks
-------------------------------
- "Structured, flexible, and robust: benchmarking and improving large language models towards more human-like behaviour in out-of-distribution reasoning tasks" Collins et al. (2022) `Paper <https://arxiv.org/abs/2205.05718>`_ `Code <https://github.com/collinskatie/structured_flexible_and_robust>`_
- "Translating natural language to planning goals with large-language models" Xie et al. (2023) `Paper <https://arxiv.org/abs/2302.05128>`_ `Code <https://github.com/clear-nus/gpt-pddl>`_
- "Faithful Chain-of-Thought Reasoning" Lyu et al. (2023) `Paper <https://arxiv.org/abs/2301.13379>`_ `Code <https://github.com/veronica320/faithful-cot>`_
- "LLM+P: Empowering Large Language Models with Optimal Planning Proficiency" Liu et al. (2023) `Paper <https://arxiv.org/abs/2304.11477>`_ `Code <https://github.com/Cranial-XIX/llm-pddl>`_
- "Dynamic Planning with a LLM" Dagan et al. (2023) `Paper <https://arxiv.org/abs/2308.06391>`_ `Code <https://github.com/itl-ed/llm-dp>`_
- "TIC: Translate-Infer-Compile for accurate 'text to plan' using LLMs and logical intermediate representations" Agarwal and Sreepathy (2024) `Paper <https://arxiv.org/abs/2402.06608>`_ `Code <N/A>`_
- "PDDLEGO: Iterative Planning in Textual Environments" Zhang et al. (2024) `Paper <https://arxiv.org/abs/2405.19793>`_ `Code <https://github.com/zharry29/nl-to-pddl>`_

Domain Translation Frameworks
---------------------------------
- "Learning adaptive planning representations with natural language guidance" Wong et al. (2023) `Paper <https://arxiv.org/abs/2312.08566>`_ `Code <N/A>`_
- "Leveraging Pre-trained Large Language Models to Construct and Utilize World Models for Model-based Task Planning" Guan et al. (2023) `Paper <https://arxiv.org/abs/2305.14909>`_ `Code <https://github.com/GuanSuns/LLMs-World-Models-for-Planning>`_
- "PROC2PDDL: Open-Domain Planning Representations from Texts" Zhang et al. (2024) `Paper <https://arxiv.org/abs/2403.00092>`_ `Code <https://github.com/zharry29/proc2pddl>`_

Hybrid Translation Frameworks
---------------------------------
- "There and Back Again: Extracting Formal Domains for Controllable Neurosymbolic Story Authoring" Kelly et al. (2023) `Paper <https://ojs.aaai.org/index.php/AIIDE/article/view/27502/27275>`_ `Code <https://github.com/alex-calderwood/there-and-back>`_
- "DELTA: Decomposed Efficient Long-Term Robot Task Planning using Large Language Models" Liu et al. (2024) `Paper <https://arxiv.org/abs/2404.03275>`_ `Code <N/A>`_
- "ISR-LLM: Iterative Self-Refined Large Language Model for Long-Horizon Sequential Task Planning" Zhou et al. (2023) `Paper <https://arxiv.org/abs/2308.13724>`_ `Code <https://github.com/ma-labo/ISR-LLM>`_
- "Consolidating Trees of Robotic Plans Generated Using Large Language Models to Improve Reliability" Sakib and Sun (2024) `Paper <https://arxiv.org/abs/2401.07868>`_ `Code <N/A>`_
- "NL2Plan: Robust LLM-Driven Planning from Minimal Text Descriptions" Gestrin et al. (2024) `Paper <https://arxiv.org/abs/2405.04215>`_ `Code <https://github.com/mrlab-ai/NL2Plan>`_
- "Leveraging Environment Interaction for Automated PDDL Generation and Planning with Large Language Models" Mahdavi et al. (2024) `Paper <https://arxiv.org/abs/2407.12979>`_ `Code <N/A>`_
- "Generating consistent PDDL domains with Large Language Models" Smirnov et al. (2024) `Paper <https://arxiv.org/abs/2404.07751>`_ `Code <N/A>`_

Model Editing and Benchmarking
----------------------------------
- "Exploring the limitations of using large language models to fix planning tasks" Gragera and Pozanco (2023) `Paper <https://icaps23.icaps-conference.org/program/workshops/keps/KEPS-23_paper_3645.pdf>`_ `Code <N/A>`_
- "Can LLMs Fix Issues with Reasoning Models? Towards More Likely Models for AI Planning" Caglar et al. (2024) `Paper <https://arxiv.org/abs/2311.13720>`_ `Code <N/A>`_
- "Large Language Models as Planning Domain Generators" Oswald et al. (2024) `Paper <https://arxiv.org/abs/2405.06650>`_ `Code <https://github.com/IBM/NL2PDDL>`_
- "Planetarium: A Rigorous Benchmark for Translating Text to Structured Planning Languages" Zuo et al. (2024) `Paper <https://arxiv.org/abs/2407.03321>`_ `Code <https://github.com/batsresearch/planetarium>`_