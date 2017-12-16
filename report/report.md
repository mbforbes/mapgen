_Maxwell Forbes_<br />
_CSE 557 Final Project Report_<br />
_December 15, 2017_

[TOC]

## Introduction

### Motivation

Procedural generation affords the creation of large, authentic looking
environments with far less time and effort than manual modeling.

The domain of _urban_ procedural generation can be roughly split into three
sub-problems: layout modelling (maps and roads), building modelling (3D
geometries), and facade modelling (3D facades and textures)
\cite{vanegas2010modelling}. Exciting advances in all of these areas have led
to remarkably realistic results, such as generating cities that expand over
time \cite{weber2009interactive} and villages that grow based on their
geography \cite{emilien2012procedural}.

While procedural generation offers great gains compared to manually creating
content, a key problem still exists: the designers of such generation systems
create the algorithms by manually designing and encoding grammars that produce
realistic looking results. This process requires substantial domain expertise
and significant trial and error. In other words, procedural generation does not
remove the manual effort required to generate large cities; it simply shifts
the effort from 3D modeling to algorithm design!

However, for city layouts, freely available data from crowdsourced map projects
now exist. From this data, it may be possible to train a machine learning model
that can automatically generate city layouts without any hand-tuned grammar
rules.

In addition to simply removing the manual work of designing generation
algorithms, a machine learning model offers other pragmatic advantages to
virtual city creators. For example, a model would learn to generate cities in
the _style_ of the geographic area on which it was trained. An old European
town will present different layout patterns than a bustling metropolis like
Tokyo. A machine learning model could capture these differences simply by being
retrained on different data, without needed to re-design the parameters or
grammars of the generation algorithm.

### Task

In this project, we approach the first domain of urban procedural generation:
generating the layout for a city. Within this domain, we further restrict our
focus to the following task: given a road network and city features (like water
and parks), fill in the buildings inside of blocks. Figure TODO shows a visual
depiction of our task.

TODO: figure for task

We split this overall task into two subtasks. In the first subtask, we extract
individual blocks with their buildings laid out on top of them. The goal is to
generate the buildings for a single block at a time (Figure TODO (a)). This
problem is more constrained, and provides an early test of the model's
capabilities.

In the second subtask, we provide a larger chunk of a city as input, and ask
the model to fill in buildings in all the empty blocks provided (Figure TODO
(b)). This task is more difficult, because more buildings must be generated and
placed within the bounds of blocks. But because we also provide geographic
features like water and parks in the input, a model can potentially take
advantage of these semantic cues to generate layouts that are sensitive to
their surroundings.

TODO: figure both subtasks

## Related Work

### Inverse Procedural Modeling _and_ Shape Learning

The idea of attempting to learn the parameters of a procedural generation model
is called _inverse procedural modeling_. Though this has never been applied to
city layout generation, it has been explored by several authors in other
domains.

Wu et al. (2014) learn a split grammar for facades, preferring shorter
descriptions as better representations of the grammar \cite{wu2013inverse}.
Though it does not appear to use machine learning, _Inverse Procedural Modeling
by Automatic Generation of L-Systems_ (2010) propose an approach for
reverse-engineering the parameters for an L-system (grammar) given input (in
their case, 2D vector images) that was generated from one
\cite{vst2010inverse}.

Other authors have used graphical models to learn how to generate shapes and
textures. Fan and Wonka (2016) learned a garphical model to generate 3D
buildings and facades \cite{fan2016probabilistic}. Martinovic and Gool (2013)
learn a 2D context-free grammar (CFG) from a set of labeled facades. In _A
Probabilistic Model for Component-Based Shape Synthesis_ (2012)
\cite{kalogerakis2012probabilistic}, the authors learn a graphical model
trained on hand-modeled 3D shapes (like a dinosaur or a chair) in order to
generate their own novel meshes. Toshev et al. (2010) take inspiration from
classical natural language processing, and learn the parameters of a parsing
model to map point clouds that represent roofs to a hierarchy of the roof's
components (e.g., main roof, hood over window, shed roof, etc.)
\cite{toshev2010detecting}.

### City Modeling

Though these works do not use machine learning or inverse procedural
generation, it is worth briefly touching upon city generation literature.
Several papers present tools for editing or expanding a set of aerial images of
cities. Aliaga et al. (2008, a) present a tool for making edits to an urban
layout and generate roads and parcels to fit into the edited regions
\cite{aliaga2008interactiveA}. In a followup work _(Aglia et al., 2008 b)_
demonstrate another tool that, given an example image, synthesizes a new street
network, and pastes in segments of the input image that fit well with the new
road network \cite{aliaga2008interactiveB}.

Other work focuses on generating cities from scratch. Weber et al. (2009)
simulate a city's growth over time, taking into account population growth and
the according land use evolution \cite{weber2009interactive}. In _Procedural
Generation of Parcels in Urban Modeling_ (2012) \cite{vanegas2012procedural},
the authors develop an algorithm for automatically splitting blocks (the spaces
carved out by road networks) into parcels (areas of land ownership). Finally,
Nishida et al. (2016) present a tool for editing road networks that takes into
account the style and layout of example data \cite{nishida2016example}.

## Dataset Creation

To the best of our knowledge, no previous work attempt the task of generating
city layouts using machine learning. Because of this, a significant portion of
the project time was spent collecting and preprocessing the data. For that
reason, this section of the report gives a brief overview of this process.
